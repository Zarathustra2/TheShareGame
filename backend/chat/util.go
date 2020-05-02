package main

import (
	"github.com/getsentry/sentry-go"
	"github.com/gorilla/websocket"
)

// Msg represents a message which is send to a user via websocket
type Msg struct {
	Data interface{} `json:"data"`
	Type MsgType     `json:"type"`
}

// MsgType represents the typ of the event which gets sent to the user over the websocket
// Should probably rename it to EventTyp...
// TODO
type MsgType int

func (m MsgType) String() string {
	return []string{"ChatMessage", "Event"}[m]
}

const (

	// ChatMsg is the type of a regular chat message
	ChatMsg MsgType = iota

	// EventMsg is the type of an event which got consumed by the redis watcher
	// adn then gets sent to the user.
	EventMsg
)

// Sends given data to a websocket.
// Given the MsgType it serializes the data and sends it to the connection.
func sendToWs(data interface{}, msgType MsgType, clients ...*websocket.Conn) {

	msg := Msg{data, msgType}
	for _, ws := range clients {
		if err := ws.WriteJSON(msg); err != nil {

			// In most cases the websocket has already been closed
			// or in other users, the user has closed his connection by
			// closing the browser for instance.
			// If this is not the case, we log the error
			if err.Error() != "websocket: close sent" {
				log.Warnf("Could not sent json to ws, error: %v", err)
				sentry.CaptureException(err)
			}
			clearMaps(ws)
		}

	}
}

// Keys returns all Keys of a websocket map
func Keys(m map[*websocket.Conn]bool) []*websocket.Conn {
	keys := make([]*websocket.Conn, len(m))
	i := 0
	for k := range m {
		keys[i] = k
		i++
	}
	return keys
}
