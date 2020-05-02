package main

import (
	"context"
	"fmt"
	"net/http"
	"os"

	"github.com/getsentry/sentry-go"
	"github.com/sirupsen/logrus"

	"github.com/jackc/pgx/v4"
)

var (

	// defaultValues for the database connection
	defaultValues = map[string]string{
		"POSTGRES_DB":       "tsg_db",
		"POSTGRES_USER":     "tsg_user",
		"POSTGRES_PASSWORD": "tsg_password",
		"POSTGRES_HOST":     "localhost",
		"POSTGRES_PORT":     "5432",
		"REDIS_ADDR":        "localhost:6379",
		"REDIS_PASSWORD":    "",
		"GO_SENTRY_DSN":     "",
	}

	ctx = context.Background()

	// TODO: Write tests with a mocked pqConn which implements the pqConn interface.
	// TODO: Or create a database and test against a real database
	pqConn *pgx.Conn

	log = logrus.New()
)

func main() {

	connectLoggerWithSentry()

	var err error
	pqConn, err = pgx.Connect(ctx, createDbConnectionString())
	if err != nil {
		log.Fatalf("Unable to connect to database: %v\n", err)
		sentry.CaptureException(err)
		os.Exit(1)
	}

	log.Info("Connected to database!")
	defer pqConn.Close(ctx)

	// Start routine for sending chat messages to all connected clients
	go handleMessages()

	// Start routine which watches redis for new events.
	go watchRedisNotifiyList()

	http.HandleFunc("/ws", handleConnections)

	log.Info("http server started on :8412")

	err = http.ListenAndServe(":8412", nil)
	if err != nil {
		log.Fatalf("ListenAndServe: %s\n", err)
		sentry.CaptureException(err)
	}
}

// createDbConnectionString returns the string for the connection to the postgres database
func createDbConnectionString() string {
	dbName := getEnvOrDefaultValue("POSTGRES_DB")
	dbUser := getEnvOrDefaultValue("POSTGRES_USER")
	dbPassword := getEnvOrDefaultValue("POSTGRES_PASSWORD")
	dbHost := getEnvOrDefaultValue("POSTGRES_HOST")
	dbPort := getEnvOrDefaultValue("POSTGRES_PORT")

	log.Infof("Host: %s, DB: %s", dbHost, dbName)

	return fmt.Sprintf("postgres://%s:%s@%s:%s/%s", dbUser, dbPassword, dbHost, dbPort, dbName)

}

// getEnvOrDefautlValue returns for a given key either the environment value if set
// or a defaultValue if the env value is not set
func getEnvOrDefaultValue(key string) string {
	val := os.Getenv(key)

	if val == "" {
		log.Infof("%s is not set, using default value now!", key)
		var ok bool
		if val, ok = defaultValues[key]; !ok {
			msg := fmt.Sprintf("Key %s not present in map", key)
			log.Warnln(msg)
			sentry.CaptureMessage(msg)
		}

	}

	return val
}

// connectLoggerWithSentry connects all logging events with sentry
// so all erros and warnings get sent to sentry
func connectLoggerWithSentry() {

	dsn := getEnvOrDefaultValue("GO_SENTRY_DSN")

	if dsn == "" {
		log.Warnln("Sentry dsn not set!")
		return
	}

	err := sentry.Init(sentry.ClientOptions{
		Dsn: dsn,
	})
	if err != nil {
		log.Warnf("sentry.Init: %s", err)
	}

}
