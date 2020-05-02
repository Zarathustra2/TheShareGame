package main

import (
	"context"
	"github.com/jackc/pgx/v4"
	"os"
	"testing"
)

func mustConnectString(t testing.TB) *pgx.Conn {
	connString := os.Getenv("TEST_CHAT_DB_CONN")
	if connString == "" {
		connString = "host=/var/run/postgresql database=tsg_test_chat"
	}
	conn, err := pgx.Connect(context.Background(), connString)
	if err != nil {
		t.Fatalf("Unable to establish connection: %v", err)
	}
	return conn
}

func closeConn(t testing.TB, conn *pgx.Conn) {
	err := conn.Close(context.Background())
	if err != nil {
		t.Fatalf("conn.Close unexpectedly failed: %v", err)
	}
}
