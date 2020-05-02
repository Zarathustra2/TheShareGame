package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/go-redis/redis/v7"
)

const notifyChannelName = "TSG_NOTIFY"

var userCountEvents = make(map[int]int)

// Event represents an event which is meant to be sent to an user.
type Event struct {
	UserID int    `json:"user_id"`
	Typ    string `json:"typ"`
	Msg    string `json:"msg"`
}

func (e *Event) String() string {
	return fmt.Sprintf("User-id: %d, Typ: %s", e.UserID, e.Typ)
}

// Watches in redis the notfiy list.
// The django backend stores event which are meant to be sent
// a specific user.
//
// If an event gets stored in the list in redis,
// watchRedisNotifiyList() consumes the event.
//
// Afterwards, the event gets sent to the user, if
// the user is currently online and has an active websocket connection.
func watchRedisNotifiyList() {

	log.Info("Connecting with Redis...")
	client, err := connectRedis()

	if err != nil {
		log.Fatalf("Failed to connect with redis, err: %s\n", err)
		sentry.CaptureException(err)
	}

	log.Infoln("Successfully connected with Redis, now listening for tasks!")

	// Start goroutine which resets the maximum of events per user
	go func() {
		log.Infoln("Started go routine for cleaning the limits for each user!")
		for {
			userCountEvents = make(map[int]int)
			time.Sleep(time.Millisecond * 500)
		}
	}()

	for {

		result, err := client.BLPop(0, notifyChannelName).Result()

		if err != nil {
			log.Fatalf("Could not read from redis list, err: %s\n", err)
			sentry.CaptureException(err)
		}

		var event Event
		err = json.Unmarshal([]byte(result[1]), &event)
		if err != nil {
			log.Warnf("Could not unmarshal json: %s\n", err)
			sentry.CaptureException(err)
			continue
		}

		// We could also think about accumlating events per user id in a map.
		// Then start for each id in the map a goroutine which sends the events in a given rate.
		if !limitEventsReached(event.UserID) {
			log.Infof("Got Event: %s. Now sending event to user\n", event.String())
			sendEvent(event)
		} else {
			log.Infof("User with id %d already got the maximum of events. Not sending event!\n", event.UserID)
		}
	}

}

// limitEventsReached returns true if a user has reached his maximum number of notifications
// and thus he/she should not reach another notifciation.
//
// The reason for that is, that we dont want to flood the user with notifications.
func limitEventsReached(userID int) bool {

	_, ok := userCountEvents[userID]
	if !ok {
		userCountEvents[userID] = 1
		return false
	}

	userCountEvents[userID]++

	return userCountEvents[userID] > 5

}

func connectRedis() (*redis.Client, error) {
	client := redis.NewClient(&redis.Options{

		// TODO: Read from env
		Addr:     getEnvOrDefaultValue("REDIS_ADDR"),
		Password: getEnvOrDefaultValue("REDIS_PASSWORD"), // no password set
		DB:       0,                                      // use default DB
	})
	_, err := client.Ping().Result()
	return client, err
}

// sendEvent sends an event to the user specified in the event
func sendEvent(event Event) {
	ws, ok := connections[event.UserID]
	if !ok {
		log.Infof("User with id %d not connected\n", event.UserID)
		return
	}

	sendToWs(event, EventMsg, ws)

}
