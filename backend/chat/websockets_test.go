package main

import (
	"reflect"
	"testing"
	"time"
)

func Test_reverse(t *testing.T) {
	type args struct {
		msg []Message
	}
	tests := []struct {
		name string
		args args
		want []Message
	}{
		{"", args{[]Message{
			{
				Text: "Hello World",
				User: User{"Max", 1, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   0,
			},
			{
				Text: "What's up?",
				User: User{"Marie", 2, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   1,
			},
			{
				Text: "Nothing much, just testing",
				User: User{"Max", 1, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   2,
			},
		}}, []Message{
			{
				Text: "Nothing much, just testing",
				User: User{"Max", 1, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   2,
			},

			{
				Text: "What's up?",
				User: User{"Marie", 2, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   1,
			},
			{
				Text: "Hello World",
				User: User{"Max", 1, true, ""},
				Time: time.Time{},
				Room: Room{1, "Global"},
				ID:   0,
			},
		}},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := reverse(tt.args.msg); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("reverse() = %v, want %v", got, tt.want)
			}
		})
	}
}
