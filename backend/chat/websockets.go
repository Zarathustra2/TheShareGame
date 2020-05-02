// Copyright 2020 Dario Heinisch. All rights reserved.
// Use of this source code is governed by a AGPL-3.0
// license that can be found in the LICENSE.txt file.

package main

import (
	"fmt"
	"net/http"
	"strconv"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/gorilla/websocket"
)

var (

	// Map to hold the connected clients
	clients = make(map[*websocket.Conn]bool)

	// Channel to hold the messages which need to be sent out
	broadcast = make(chan Message)

	// Map to save which client has which token
	users = make(map[*websocket.Conn]User)

	// Map to save which user_id is connected over which connection
	connections = make(map[int]*websocket.Conn)

	// Upgrades a normal Request to a websocket
	upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin: func(r *http.Request) bool {
			arr := r.Header["Origin"]

			if len(arr) == 0 {
				log.Info("Origin length was 0!")
				return false
			}

			origin := arr[0]

			log.Info(origin)

			allowedOrigins := []string{"https://www.thesharegame.com", "127.0.0.1:8412", "http://localhost:8080"}

			for _, e := range allowedOrigins {
				if e == origin {
					return true
				}
			}

			msg := fmt.Sprintf("Origin %s is not allowed!\n", origin)
			log.Infof(msg)
			sentry.CaptureMessage(msg)
			return false
		},
	}
)

// handleConnections handles a new incoming register connection.
// It upgrades the connection to a websocket connection.
// It then waits for messages from the client
//
// If the client does not provide a valid token
// he will be rejected
func handleConnections(w http.ResponseWriter, r *http.Request) {
	token := r.URL.Query().Get("token")

	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Warn(err)
		sentry.CaptureException(err)
		return
	}

	defer ws.Close()

	// get the User of the connection
	user, err := getUser(pqConn, token)

	if err != nil {
		log.Warnf("handleConnections: %s\n", err)
	} else {
		users[ws] = user
		connections[user.ID] = ws
	}

	clients[ws] = true
	log.Infof("New Client registered! Total clients: %d\n", len(clients))

	amountStr := r.URL.Query().Get("amount")
	sendLastChatMessages(amountStr, ws)

	// Only valid users should be able to chat
	if token == "" || !tokenIsValid(pqConn, token) {
		// Bring the non authenticated in en empty loop
		// so the connection is still valid
		// TODO: Is this the right way?
		// This seems so wrong....
		select {}
	}

	for {

		var msg Message

		err := ws.ReadJSON(&msg)
		if err != nil {
			log.Warnf("Could not read json from ws, error: %v", err)
			sentry.CaptureException(err)
			clearMaps(ws)
			break
		}

		log.Debug("New message received! Broadcasting now!")

		msg.Time = time.Now()
		msg.User = users[ws]

		if err := msg.save(pqConn); err != nil {

			log.Warnf("Could not save message, error was: %s\n", err)
			sentry.CaptureException(err)

			// Skip broadcasting message as saving in the database was unsuccessful
			continue
		}

		broadcast <- msg
	}

}

// handleMessages sends out messages to all clients if there is one available
// in the messages channel
func handleMessages() {
	for {

		msg := <-broadcast
		log.Infof("Sending msg to %d clients", len(clients))
		arr := Keys(clients)
		sendToWs(msg, ChatMsg, arr...)
	}
}

func clearMaps(ws *websocket.Conn) {
	delete(clients, ws)
	u, ok := users[ws]
	if ok {
		delete(connections, u.ID)
	}
	delete(users, ws)
	_ = ws.Close()
}

func reverse(msg []Message) []Message {
	last := len(msg) - 1
	for i := 0; i < len(msg)/2; i++ {
		msg[i], msg[last-i] = msg[last-i], msg[i]
	}
	return msg
}

func sendLastChatMessages(amountStr string, ws *websocket.Conn) {
	var amount int
	var err error

	if amountStr == "" {
		amount = 10
	} else {
		amount, err = strconv.Atoi(amountStr)
		if err != nil {
			log.Warnf("Could not convert string to integer! %s\n", err)
			amount = 10
		}
	}

	// get last n messages and send them to the client
	// TODO Pass the room id as well
	messages, err := getChatMessages(pqConn, amount)
	if err != nil {
		log.Fatalf("Could not get messages, error was %s", err)
	} else {
		for _, m := range reverse(messages) {
			sendToWs(m, ChatMsg, ws)
		}
	}
}
