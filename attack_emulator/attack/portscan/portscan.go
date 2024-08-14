package portscan

import (
	"context"
	"fmt"
	"net"
	"os/exec"
	"strconv"
	"strings"
	"sync"
	"time"

	"golang.org/x/sync/semaphore"
)

type PortScanner struct {
	ip   string
	lock *semaphore.Weighted
}

func Ulimit() int64 {
	out, err := exec.Command("bash", "-c", "ulimit -n").Output()
	if err != nil {
		panic(err)
	}

	s := strings.TrimSpace(string(out))

	i, err := strconv.ParseInt(s, 10, 64)
	if err != nil {
		panic(err)
	}

	return i
}

func ScanPort(ip string, port int, timeout time.Duration) bool {
	target := fmt.Sprintf("%s:%d", ip, port)
	//Instead of using <$0>
	var conn net.Conn
	var err error
	for attempts := 0; attempts < 3; attempts++ {
		conn, err = net.DialTimeout("tcp", target, timeout)
		if err != nil {
			if strings.Contains(err.Error(), "too many open files") {
				time.Sleep(timeout)
				// ScanPort(ip, port, timeout) <$0>
				continue
			} else {
				// fmt.Println(port, "closed")
			}
			return false
		}
		break
	}

	conn.Close()
	fmt.Println(port, "open")
	return true
}

func (ps *PortScanner) Start(f, l int, timeout time.Duration) []int {
	// https://gobyexample.com/waitgroups
	wg := sync.WaitGroup{}
	var mutex sync.Mutex
	open_port := make([]int, 0)
	for port := f; port <= l; port++ {
		ps.lock.Acquire(context.TODO(), 1) //Acquire one permit token to access common resource
		wg.Add(1)
		go func(port int) {
			defer ps.lock.Release(1)
			defer wg.Done()
			isOpen := ScanPort(ps.ip, port, timeout)
			if isOpen {
				mutex.Lock() //Muter.Lock and Unlock to prevent data race in shared resource
				open_port = append(open_port, port)
				mutex.Unlock()
			}
		}(port)
	}
	defer wg.Wait()
	return open_port

}

func RunPortscan(host string) {
	ps := &PortScanner{
		ip:   host, //"127.0.0.1"
		lock: semaphore.NewWeighted(Ulimit()),
	}
	// ps.Start(1, 65535, 500*time.Millisecond)
	open_port := ps.Start(1, 65535, 500*time.Millisecond)
	for _, port := range open_port {
		fmt.Printf("%d, ", port)
	}
	fmt.Printf("\n")
	fmt.Printf("Total of %d ports opened", len(open_port))

}
