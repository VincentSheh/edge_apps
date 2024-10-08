package dos_test

import (
	"attack/dos"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"testing"
	"time"

	freeport "github.com/Konstantin8105/FreePort"
	// dos "github.com/Konstantin8105/dos"
	// freeport "github.com/Konstantin8105/FreePort"
)

func TestNewdos(t *testing.T) {
	d, err := dos.New("http://127.0.0.1", 1)
	if err != nil {
		t.Error("Cannot create a new dos structure. Error = ", err)
	}
	if d == nil {
		t.Error("Cannot create a new dos structure")
	}
}

func Testdos(t *testing.T) {
	port, err := freeport.Get()
	if err != nil {
		t.Errorf("Cannot found free tcp port. Error = %v", err)
	}
	createServer(port, t)

	url := "http://127.0.0.1:" + strconv.Itoa(port)
	d, err := dos.New(url, 1000)
	if err != nil {
		t.Error("Cannot create a new dos structure")
	}
	d.Run()
	time.Sleep(time.Second)
	d.Stop()
	success, amount := d.Result()
	if success == 0 || amount == 0 {
		t.Errorf("Negative result of dos attack.\n"+
			"Success requests = %v.\n"+
			"Amount requests = %v", success, amount)
	}
	t.Logf("Statistic: %d %d", success, amount)
}

// Create a simple go server
func createServer(port int, t *testing.T) {
	go func() {
		http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
			fmt.Fprintf(w, "Hi there, I love %s!", r.URL.Path[1:])
		})
		if err := http.ListenAndServe(":"+strconv.Itoa(port), nil); err != nil {
			t.Fatalf("Server is down. %v", err)
		}
	}()
}

func TestWorkers(t *testing.T) {
	_, err := dos.New("127.0.0.1", 0)
	if err == nil {
		t.Error("Cannot create a new dos structure")
	}
}

func TestUrl(t *testing.T) {
	_, err := dos.New("some_strange_host", 1)
	if err == nil {
		t.Error("Cannot create a new dos structure")
	}
}

func ExampleNew() {
	workers := 1000
	d, err := dos.New("http://127.0.0.1:80", workers)
	if err != nil {
		panic(err)
	}
	d.Run()
	time.Sleep(time.Second)
	d.Stop()
	fmt.Fprintf(os.Stdout, "dos attack server: http://127.0.0.1:80\n")
	// Output:
	// dos attack server: http://127.0.0.1:80
}
