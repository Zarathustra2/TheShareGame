package main

import (
	"encoding/json"
	"github.com/magiconair/properties/assert"
	"testing"
	"time"
)

func Test_MsgSerializesWithEvent(t *testing.T) {
	msg := Msg{
		Data: Event{
			UserID: 1,
			Typ:    "hello",
			Msg:    "Hello",
		},
		Type: EventMsg,
	}
	b, err := json.Marshal(msg)
	if err != nil {
		t.Error(err)
	}
	assert.Equal(t, string(b), `{"data":{"user_id":1,"typ":"hello","msg":"Hello"},"type":1}`)
}

func Test_MsgSerializesWithChatMsg(t *testing.T) {
	msg := Msg{
		Data: Message{
			Text: "Lorem",
			User: User{},
			Time: time.Time{},
			Room: Room{},
			ID:   0,
		},
		Type: ChatMsg,
	}

	b, err := json.Marshal(msg)
	if err != nil {
		t.Error(err)
	}

	assert.Equal(t, string(b), `{"data":{"message":"Lorem","user":{"username":"","id":0},"time":"0001-01-01T00:00:00Z","room":{"id":0,"name":""},"id":0},"type":0}`)

}

func TestMsgType_String(t *testing.T) {
	tests := []struct {
		name string
		m    MsgType
		want string
	}{
		{"chat-msg", 0, "ChatMessage"},
		{"event", 1, "Event"},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.m.String(); got != tt.want {
				t.Errorf("String() = %v, want %v", got, tt.want)
			}
		})
	}
}
