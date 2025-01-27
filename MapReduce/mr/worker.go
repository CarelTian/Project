package mr

import (
	//"bufio"
	"encoding/json"
	"fmt"
	"hash/fnv"
	"io"
	"log"
	"sort"

	//"net/http"
	"net/rpc"
	"os"
	"time"
)

type ByKey []KeyValue

// for sorting by key.
func (a ByKey) Len() int           { return len(a) }
func (a ByKey) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByKey) Less(i, j int) bool { return a[i].Key < a[j].Key }
// Map functions return a slice of KeyValue.
type KeyValue struct {
	Key   string
	Value string
}

// use ihash(key) % NReduce to choose the reduce
// task number for each KeyValue emitted by Map.
func ihash(key string) int {
	h := fnv.New32a()
	h.Write([]byte(key))
	return int(h.Sum32() & 0x7fffffff)
}

// main/mrworker.go calls this function.
func Worker(mapf func(string, string) []KeyValue,
	reducef func(string, []string) string) {
OuterLoop:
	for {
		task := requestTask()
		switch task.Type {
		case MAP:
			handleMap(&task, mapf)
		case REDUCE:
			handleReduce(&task, reducef)
		default:
			break OuterLoop
		}
		time.Sleep(100 * time.Millisecond)
	}
	// Your worker implementation here.

	// uncomment to send the Example RPC to the coordinator.
	// CallExample()
}

func requestTask() Task {
	args := RequestTaskArgs{}
	reply := RequestTaskReply{}

	ok := call("Coordinator.RequestTask", &args, &reply)
	if !ok {
		return Task{}
	}
	return reply.Task
}
func handleMap(task *Task, mapf func(string, string) []KeyValue) {
	filename := task.Filename
	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("cannot open %v", filename)
	}
	content, err := io.ReadAll(file)
	if err != nil {
		log.Fatalf("cannot read %v", filename)
	}
	file.Close()
	kva := mapf(filename, string(content))
	buckets := make(map[int][]KeyValue)
	nReduce := task.NReduce
	for _, kv := range kva {
		index := ihash(kv.Key) % nReduce
		buckets[index] = append(buckets[index], kv)
	}
	for i := 0; i < nReduce; i++ {
		tempfile := getTempName(i,task.ID)
		file, err := os.Create(tempfile)
		if err != nil {
			fmt.Println("creat file failed")
		}
		defer file.Close()
		encoder := json.NewEncoder(file)
		kvs := buckets[i]
		for _, kv := range kvs {
			if err := encoder.Encode(kv); err != nil {
				fmt.Println("write file failed")
			}
		}
	}
	args := TaskDoneArgs{ID: task.ID}
	reply := TaskDoneReply{}

	ok := call("Coordinator.TaskDone", &args, &reply)
	if !ok {
		fmt.Println("RPC TaskDone failed")
	}
}
func handleReduce(task *Task, reducef func(string, []string) string) {
	args := TaskDoneArgs{ID: task.ID}
	reply := TaskDoneReply{}
	nmap:=task.NMap
	intermediate:=make([]KeyValue, 0)
	for i:=0;i<nmap;i++{
		rfile,err:=os.Open(getTempName(task.ID,i))
		if err!=nil{
			fmt.Println(err)
		}
		dec:=json.NewDecoder(rfile)
		for {
			var kv KeyValue
			if err := dec.Decode(&kv); err != nil {
				break
			}
			intermediate = append(intermediate, kv)
		}
		sort.Sort(ByKey(intermediate))
		wfile, err :=os.Create(getFileName(task.ID))
		if err!=nil{
			fmt.Println(err)
		}
		i := 0
		for i < len(intermediate) {
			j := i + 1
			for j < len(intermediate) && intermediate[j].Key == intermediate[i].Key {
				j++
			}
			values := []string{}
			for k := i; k < j; k++ {
				values = append(values, intermediate[k].Value)
			}
			output := reducef(intermediate[i].Key, values)
	
			// this is the correct format for each line of Reduce output.
			fmt.Fprintf(wfile, "%v %v\n", intermediate[i].Key, output)
			i = j
		}

	}
	for i:=0;i<nmap;i++{
		os.Remove(getTempName(task.ID,i))
	}
	ok := call("Coordinator.TaskDone", &args, &reply)
	if !ok {
		fmt.Println("RPC TaskDone failed")
	}

}

func getTempName(i int, j int) string {
	return fmt.Sprintf("mr-%d-%d", i,j)
}
func getFileName(i int) string {
	return fmt.Sprintf("mr-out-%d", i)
}

// example function to show how to make an RPC call to the coordinator.
//
// the RPC argument and reply types are defined in rpc.go.
func CallExample() {

	// declare an argument structure.
	args := ExampleArgs{}

	// fill in the argument(s).
	args.X = 99

	// declare a reply structure.
	reply := ExampleReply{}

	// send the RPC request, wait for the reply.
	// the "Coordinator.Example" tells the
	// receiving server that we'd like to call
	// the Example() method of struct Coordinator.
	ok := call("Coordinator.Example", &args, &reply)
	if ok {
		// reply.Y should be 100.
		fmt.Printf("reply.Y %v\n", reply.Y)
	} else {
		fmt.Printf("call failed!\n")
	}
}

// send an RPC request to the coordinator, wait for the response.
// usually returns true.
// returns false if something goes wrong.
// func call(rpcname string, args interface{}, reply interface{}) bool {
// 	// c, err := rpc.DialHTTP("tcp", "127.0.0.1"+":1234")
// 	//var connected = "200 Connected to Go RPC"
// 	var client *rpc.Client
// 	sockname := coordinatorSock()
// 	conn, err := net.DialTimeout("unix", sockname, 5*time.Second)
// 	if err != nil {
// 		fmt.Println("dialing failed:", err)
// 		return false
// 	}
// 	defer conn.Close()
// 	io.WriteString(conn, "CONNECT /_goRPC_ HTTP/1.0\n\n")
// 	conn.SetReadDeadline(time.Now().Add(5* time.Second))
// 	http.ReadResponse(bufio.NewReader(conn), &http.Request{Method: "CONNECT"})
// 	client = rpc.NewClient(conn)
// 	done := make(chan error, 1)
// 	go func() {
// 		done <- client.Call(rpcname, args, reply)
// 	}()
// 	select {
// 	case err := <-done:
// 		if err == nil {
// 			return true
// 		}
// 		fmt.Println("RPC call failed:", err)
// 		return false
// 	case <-time.After(5* time.Second): 
// 		fmt.Println("RPC call timed out")
// 		return false
// 	}
// }
func call(rpcname string, args interface{}, reply interface{}) bool {
	// c, err := rpc.DialHTTP("tcp", "127.0.0.1"+":1234")
	sockname := coordinatorSock()
	c, err := rpc.DialHTTP("unix", sockname)
	if err != nil {
		log.Fatal("dialing:", err)
	}
	defer c.Close()

	err = c.Call(rpcname, args, reply)
	if err == nil {
		return true
	}
	return false
}