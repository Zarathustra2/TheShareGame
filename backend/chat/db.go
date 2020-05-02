package main

import (
	"context"
	"errors"
	"time"

	"github.com/getsentry/sentry-go"
	"github.com/jackc/pgx/v4"
)

// User represents a user account
type User struct {
	Username string `json:"username"`
	ID       int    `json:"id"`

	// IsActive signals whether a user can perform any actions
	IsActive bool `json:"-"`

	// The token used for authentication
	Token string `json:"-"`
}

// Room represents a chat room
type Room struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
}

// Message defines a chat message which has been sent
type Message struct {

	// The actual message
	Text string `json:"message"`

	// The author of the message
	User User `json:"user"`

	// The Time the message has been sent
	Time time.Time `json:"time"`

	// The Room the chat message was sent in
	Room Room `json:"room"`

	ID int `json:"id"`
}

// tokenIsValid checks whether the token exists in the database.
// If it does, it returns true, otherwise false
func tokenIsValid(conn *pgx.Conn, token string) bool {
	var exists int
	err := conn.QueryRow(ctx, "select 1 from authtoken_token where key=$1", token).Scan(&exists)
	switch err {
	case pgx.ErrNoRows:
		log.Printf("No user with token %s exists\n", token)
		return false

	case nil:
		return true

	default:
		log.Fatalf("QueryRow failed: %v\n", err)
		sentry.CaptureException(err)
		return false
	}
}

// save saves a message in the database
func (m *Message) save(conn *pgx.Conn) error {

	if len(m.Text) > 100 {
		return errors.New("Text was longer than 100 chars, could not save!")
	}

	m.Time = time.Now()

	// If room is not set, set to default Chat room
	// 1 is the gloabl chat room which is always the default room
	// TODO If sent to another room, check if the user is part of that room!
	if m.Room == (Room{}) {
		m.Room = Room{ID: 1}
	}

	if m.User == (User{}) {
		return errors.New("User cannot be empty")
	}

	_, err := conn.Exec(context.Background(), "insert into chat_message(text, created, room_id, user_id) values($1, $2, $3, $4)", m.Text, m.Time, m.Room.ID, m.User.ID)

	return err
}

// getChatMessages returns the last N chat messages sorted by id.
// N can be specified by the parameter amount
func getChatMessages(conn *pgx.Conn, amount int) ([]Message, error) {

	// TODO: Add where clause for room id
	query := `
			SELECT "chat_message"."text", "chat_message"."id", "chat_message"."user_id", "chat_message"."room_id", "chat_message"."created", "user"."username", "chat_room"."name"
			FROM "chat_message"
			INNER JOIN "user" ON ("chat_message"."user_id" = "user"."id")
			INNER JOIN "chat_room" ON ("chat_message"."room_id" = "chat_room"."id")
			order by "chat_message"."id" desc limit($1)
		`
	rows, _ := conn.Query(context.Background(), query, amount)

	messages := make([]Message, 0)

	if err := rows.Err(); err != nil {
		return nil, err
	}

	for rows.Next() {
		var msg Message
		err := rows.Scan(&msg.Text, &msg.ID, &msg.User.ID, &msg.Room.ID, &msg.Time, &msg.User.Username, &msg.Room.Name)
		if err != nil {
			return nil, err
		}
		messages = append(messages, msg)
	}

	return messages, nil
}

// getUser returns the user who is associated with the given token
func getUser(conn *pgx.Conn, token string) (User, error) {
	query := `
		 SELECT "user"."id", "user"."username", "user"."is_active" FROM "user"
		 INNER JOIN "authtoken_token" ON ("user"."id" = "authtoken_token"."user_id")
		 WHERE "authtoken_token"."key" = ($1)
	`

	var user User

	err := conn.QueryRow(context.Background(), query, token).Scan(&user.ID, &user.Username, &user.IsActive)

	switch err {

	case pgx.ErrNoRows:
		return user, errors.New("No user with the token exists")

	case nil:

		// Check whether the user is marked as active
		// and can perform any actions
		if !user.IsActive {
			return user, errors.New("User is not active")
		}
		// user.Token = token
		return user, nil

	default:
		return user, err
	}

}
