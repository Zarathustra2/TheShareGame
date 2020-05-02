package main

import (
	"encoding/json"
	"github.com/stretchr/testify/assert"
	"testing"
)

/*func Test_tokenIsValid(t *testing.T) {
	conn := mustConnectString(t)
	defer closeConn(t, conn)
}*/

func Test_UserTokenAndIsValidNotSerialized(t *testing.T) {
	user := User{
		Username: "Max",
		ID:       1,
		IsActive: true,
		Token:    "some-token",
	}

	data, err := json.Marshal(user)
	if err != nil {
		t.Errorf("%s", err)
	}

	var userUnmarshaled User
	err = json.Unmarshal(data, &userUnmarshaled)
	if err != nil {
		t.Errorf("%s", err)
	}

	assert.Equal(t, userUnmarshaled.ID, user.ID)
	assert.Equal(t, userUnmarshaled.Username, user.Username)

	// Default Value of the field
	assert.False(t, userUnmarshaled.IsActive)
	assert.Equal(t, userUnmarshaled.Token, "")

}
