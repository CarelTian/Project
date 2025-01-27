package mr

import (
	"log"
	"math"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"sync"
	"time"
)


type Coordinator struct {
	// Your definitions here.
	state 	string
	nMap 	int
	nReduce int
	taskQue chan *Task
	taskMap map[int]*Task
	mu 		sync.Mutex
}
type Task struct{
	ID 		int
	Type	string
	Filename string
	NReduce int
	NMap    int
	Deadline int64
}

// Your code here -- RPC handlers for the worker to call.

//
// an example RPC handler.
//
// the RPC argument and reply types are defined in rpc.go.
//
func (c *Coordinator) Example(args *ExampleArgs, reply *ExampleReply) error {
	reply.Y = args.X + 1
	return nil
}


//
// start a thread that listens for RPCs from worker.go
//
func (c *Coordinator) server() {
	rpc.Register(c)
	rpc.HandleHTTP()
	//l, e := net.Listen("tcp", ":1234")
	sockname := coordinatorSock()
	os.Remove(sockname)
	l, e := net.Listen("unix", sockname)
	if e != nil {
		log.Fatal("listen error:", e)
	}
	go http.Serve(l, nil)
}
const (
	MAP ="map"
	REDUCE="reduce"
	QUIT="quit"
	TIME_OUT=10 *time.Second
)
//
// main/mrcoordinator.go calls Done() periodically to find out
// if the entire job has finished.
//
func (c *Coordinator) Done() bool {
	ret := false
	c.mu.Lock()
	ret= c.state==QUIT
	c.mu.Unlock()
	// Your code here.
	return ret
}

//
// create a Coordinator.
// main/mrcoordinator.go calls this function.
// nReduce is the number of reduce tasks to use.
//
func MakeCoordinator(files []string, nReduce int) *Coordinator {
	c := Coordinator{}
	c.nReduce = nReduce
	c.nMap = len(files)
	c.taskQue = make(chan *Task, int(math.Max(float64(len(files)), float64(nReduce))))
	c.taskMap = make(map[int]*Task)
	c.mu = sync.Mutex{}
	c.state = MAP
	for i, filename :=range files{
		task:=Task{
			ID: i,
			Type: MAP,
			Filename: filename,
			NReduce: nReduce,
			NMap: c.nMap,
			Deadline: -1,
		}
		c.taskQue <- &task
		c.taskMap[i]=&task
	}
	
	// Your code here.
	go c.changeState()
	go c.detector()
	c.server()
	return &c
}
func (c *Coordinator) detector(){
	for{
		c.mu.Lock()
		for _,task :=range c.taskMap {
			deadline:=task.Deadline
			if deadline !=-1{
				now:=time.Now().Unix()
				if(deadline<now){
					task.Deadline=-1
					c.taskQue <- task
				}
			}
		}
		c.mu.Unlock()
		time.Sleep(1*time.Second)
	}
}
func (c *Coordinator) changeState(){
	for {
		if(len(c.taskMap)==0){
			c.mu.Lock()
			if c.state==MAP{
				c.state=REDUCE
				for i:=0;i<c.nReduce;i++{
					task:=Task{
						ID: i,
						Type: REDUCE,
						Deadline: -1,
						NMap: c.nMap,
						NReduce: c.nReduce,
					}
					c.taskQue <- &task
					c.taskMap[i]= &task
				}

			}else if c.state==REDUCE{
				os.Exit(0)
			}
			c.mu.Unlock()

		}
		time.Sleep(100*time.Millisecond)
	}
}


func (c *Coordinator) RequestTask(args *RequestTaskArgs, reply *RequestTaskReply) error {
	if len(c.taskMap) != 0 {
		task := <-c.taskQue
		task.Deadline = time.Now().Add(TIME_OUT).Unix()
		reply.Task = *task
	} 
	return nil
}

func(c *Coordinator) TaskDone(args *TaskDoneArgs,reply *TaskDoneReply) error{
	c.mu.Lock()
	delete(c.taskMap,args.ID)
	c.mu.Unlock()
	return nil
}