package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"io/ioutil"
	"os"
	"strings"
	"time"
	"strconv"
	"github.com/influxdata/influxdb-client-go"
)

var lm LoadMaster


type test_struct struct {
	Test string
}


type LoadMaster struct {
	Custid int    `json:"custid"`
	Name   string `json:"name"`
	Lmclusterid   int    `json:"lmclusterid"`
	Mode string `json:"mode"`
	Lm     []struct {
		Name string `json:"name"`
		IP   string `json:"ip"`
		Model string `json:"model"`
		Firmware string `json:"firmware"`
		Cpu  struct{
		    User          int `json:"user"`
		    System        int `json:"system"`
		    Idle          int `json:"idle"`
		    Iowait        int `json:"iowait"`
		} `json:"cpu"`
		Memory  struct{
		    Memused          int `json:"memused"`
		    Percentmemused   int `json:"percentmemused"`
		    Memfree          int `json:"memfree"`
		    Percentmemfree   int `json:"percentmemfree"`
		} `json:"memory"`
		License  struct{
	        Substier        string `json:"substier"`
		    Subsexpiry      string `json:"subsexpiry"`
		    Subsexpirydays   int `json:"subsexpirydays"`
		} `json:"license"`
	} `json:"lm"`
	Vs []struct {
		IP          string `json:"ip"`
		Port        string `json:"port"`
		ID          int `json:"id"`
		Status      string `json:"status"`
		Conns       int `json:"conns"`
		Activeconns int `json:"activeconns"`
		Connrate    int `json:"connrate"`
		Rs          []struct {
			Vsid        int `json:"vsid"`
			IP          string `json:"ip"`
			Port        string `json:"port"`
			ID          int `json:"id"`
			Activeconns int `json:"activeconns"`
			Connrate    int `json:"connrate"`
			Status        string `json:"status"`
		} `json:"rs"`
	} `json:"vs"`
}

type Config struct {
     Time    int64   `json:"time"`
     Name  string  `json:"name"`
     Motd  string  `json:"motd"`
}

var lmnow LoadMaster
var lmbefore LoadMaster
// Update these to be Lists of LMS
var config Config
var filename string


func writeToInflux(lmc LoadMaster) {
    //HARD SET VALUES NEEDS TO CHANGE
  //LOCAL const token = "9GBncCCkDiQlauEUxXUuMEwW33Jxl1R6TxeQpDBc23pbiCNs94f0kTScD-x-zfkUd5I3v-7r-Ua4y_kUe04Gjw=="

  const token = "PzOZxZQ79tiT9VNV0Ngz5uI_A5FYxvTQTt6Cdzy244AL9P8ok9l_hByNLc_1woBccx0jXEvOmNs2sfWjaYWV6Q=="
  const bucket = "axf"
  const org = "kemp"
  client := influxdb2.NewClient("http://localhost:8086", token)


  // get non-blocking write client
  writeAPI := client.WriteAPI(org, bucket)
  fmt.Println(fmt.Sprintf("lmmode,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Mode=\""+lmc.Mode+"\""))
  writeAPI.WriteRecord(fmt.Sprintf("lmmode,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Mode=\""+lmc.Mode+"\""))
  fmt.Println(fmt.Sprintf("lmame,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Lmname=\""+lmc.Name+"\""))
  writeAPI.WriteRecord(fmt.Sprintf("lmname,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Lmname=\""+lmc.Name+"\""))

  // write line protocol
  // For each LM
  for _, lm := range lmc.Lm {
    fmt.Println(fmt.Sprintf("lmcpu,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname User="+strconv.Itoa(lm.Cpu.User)+",System="+strconv.Itoa(lm.Cpu.System)+",Idle="+strconv.Itoa(lm.Cpu.Idle)+",Iowait="+strconv.Itoa(lm.Cpu.Iowait)))
    fmt.Println(fmt.Sprintf("lmmem,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Used="+strconv.Itoa(lm.Memory.Percentmemused)+",Free="+strconv.Itoa(lm.Memory.Memfree)+",Memused="+strconv.Itoa(lm.Memory.Memused)))
    fmt.Println(fmt.Sprintf("lmfw,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Firmware=\""+lm.Firmware+"\""))
    //fmt.Println(fmt.Sprintf("lmsubs,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Substier=\""+lm.License.Substier+"\",Subsexpiry=\""+lm.License.Subsexpiry+"\",Subsexpirydays=\""+strconv.Itoa(lm.License.Subsexpirydays)+"\""))
    fmt.Println(fmt.Sprintf("lmsubs,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Substier=\""+lm.License.Substier+"\""))

    writeAPI.WriteRecord(fmt.Sprintf("lmcpu,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname User="+strconv.Itoa(lm.Cpu.User)+",System="+strconv.Itoa(lm.Cpu.System)+",Idle="+strconv.Itoa(lm.Cpu.Idle)+",Iowait="+strconv.Itoa(lm.Cpu.Iowait)))
    writeAPI.WriteRecord(fmt.Sprintf("lmmem,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Used="+strconv.Itoa(lm.Memory.Percentmemused)+",Free="+strconv.Itoa(lm.Memory.Memfree)+",Memused="+strconv.Itoa(lm.Memory.Memused)))
    writeAPI.WriteRecord(fmt.Sprintf("lmfw,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Firmware=\""+lm.Firmware+"\""))
    writeAPI.WriteRecord(fmt.Sprintf("lmsubs,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Substier=\""+lm.License.Substier+"\""))




    writeAPI.WriteRecord(fmt.Sprintf("lmmodel,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Model=\""+lm.Model+"\""))
    writeAPI.WriteRecord(fmt.Sprintf("lmip,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Ip=\""+lm.IP+"\""))


    // example Print lmcpu,Custid=1001,Lmclusterid=1,Name=Xname User=1,System=1,Idle=99,Iowait=0
    //BeforewriteAPI.WriteRecord(fmt.Sprintf("lmmem,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,Name=Xname Used="+strconv.Itoa(lm.Memory.Percentmemused)+",Free="+strconv.Itoa(lm.Memory.Percentmemfree)))
  }
  //writeAPI.WriteRecord(fmt.Sprintf("vsconns,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID=1 Conns=123"))
  for _, vs := range lmc.Vs {
    fmt.Println(fmt.Sprintf("VsConns,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+" Conns="+strconv.Itoa(vs.Conns)))
    writeAPI.WriteRecord(fmt.Sprintf("vsconns,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+" Conns="+strconv.Itoa(vs.Conns)))
    writeAPI.WriteRecord(fmt.Sprintf("VsActiveconns,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+" Conns="+strconv.Itoa(vs.Activeconns)))
    writeAPI.WriteRecord(fmt.Sprintf("VsConnrate,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+" Conns="+strconv.Itoa(vs.Connrate)))
    for _, rs := range vs.Rs {
        writeAPI.WriteRecord(fmt.Sprintf("RsActiveconns,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+",RSID="+strconv.Itoa(rs.ID)+" Conns="+strconv.Itoa(rs.Activeconns)))
        writeAPI.WriteRecord(fmt.Sprintf("RsConnrate,Custid="+strconv.Itoa(lmc.Custid)+",Lmclusterid=1,VSID="+strconv.Itoa(vs.ID)+",RSID="+strconv.Itoa(rs.ID)+" Conns="+strconv.Itoa(rs.Connrate)))


    }
  }

}

func recordEvent (description, custid, lmid, objectid, rule, state string) {
    currentTime := time.Now()
    f, err := os.OpenFile("/var/log/events.log", os.O_APPEND|os.O_WRONLY, 0644)
    if err != nil {
        fmt.Println(err)
        return
    }
    str := []string{currentTime.Format("2006-01-02 15:04:05"),description,custid,lmid,objectid,rule,state}
    _, err = fmt.Fprintln(f, strings.Join(str, ","))
    if err != nil {
        fmt.Println(err)
                f.Close()
        return
    }
    err = f.Close()
    if err != nil {
        fmt.Println(err)
        return
    }
    fmt.Println("file appended successfully")

}

func vsupdownrule (now, before LoadMaster, custid string)  {
    for _, nowvs := range now.Vs {
        //fmt.Println(nowvs.ID, nowvs.Status)
        for _, beforevs := range before.Vs {
                //fmt.Println(beforevs.ID, beforevs.Status)
                if (beforevs.ID == nowvs.ID){
                    if (beforevs.Status != nowvs.Status){
                        //str := []string{nowvs.ID, strconv.Itoa(now.Custid), "Your Virtual service is now in a ", nowvs.Status}
                         // joining the string by separator
                        //fmt.Println(strings.Join(str, "-"))
                        recordEvent("\"Your Virtual Service has changed state\"", strconv.Itoa(now.Custid), custid , strconv.Itoa(nowvs.ID), "VSStateChange",nowvs.Status)
                        //recordEvent(strings.Join(str, "-"))
                    }
                    break
                }
        }
    }
}


func rsupdownrule (now, before LoadMaster, custid string)  {
    for _, nowvs := range now.Vs {
        //fmt.Println(nowvs.ID, nowvs.Status)
        for _, beforevs := range before.Vs {
                if (beforevs.ID == nowvs.ID){
                    //Iternate through All RSs for changes and Exit
                    for _, nowrs := range nowvs.Rs {
                        for _, beforers := range beforevs.Rs {
                            if (beforers.ID == nowrs.ID){
                                if (beforers.Status != nowrs.Status){
                                    recordEvent("\"Your Real Server has changed state\"", strconv.Itoa(now.Custid), custid , strconv.Itoa(nowvs.ID)+strconv.Itoa(nowrs.ID), "RSStateChange",nowrs.Status)
                                }
                                break
                            }
                        }
                    }
                    break
                }
        }
    }
}

func memoryRule (now LoadMaster, before LoadMaster, threshold int) {
        var beforeint int
        var nowint int
        for _, nowlm := range now.Lm {
            for _, beforelm := range before.Lm {
                if (beforelm.Name == nowlm.Name){
                    beforeint=beforelm.Memory.Percentmemused
                    nowint=nowlm.Memory.Percentmemused
                    if ((beforeint <=  threshold) && (nowint >  threshold)){
                           //recordEvent("Your LoadMaster"+ nowlm.Name+" is seeing high Memory Usage")
                    }
                }
            }
        }
}




//
//2021-12-02 15:31:10,"Your Virtual Service has changed state",1000,1000,13,VSStateChange,up
//%{SYSLOGTIMESTAMP:time},%{QUOTEDSTRING:description},%{INT:custid},%{INT:lmid},%{INT:vsid},%{WORD:kmod},%{WORD:state}
//
//
//


// Metric Rule compars Now to Previous
//func metricrule (now, before LoadMaster)  {
// Check Metric Value and if it crossed a threshold.
// Reset when threshold changed
// Pass in Threshold?
// Connections Per Second, CPU, Memory
// Return a JSON
// TYPE: Trigger, Resolve, Type: CPU High, VS Down,
//}
// Dispersion Rule compars Multiple Metrics at the same time
//func disprule (now, before LoadMaster)  {
//# Lumpy Balancing
//# RTT Comparisons
//# Return a JSON
//# TYPE: Trigger, Resolve, Type: CPU High, VS Down,
//}



func parseGhPost(rw http.ResponseWriter, request *http.Request) {

    switch request.Method {
      case "GET":
            //fmt.Println("GET",request.URL.Path)
            fmt.Printf("-------- SERVING OF LM CONFIG --------\n")
            filename= "config_"+strings.ReplaceAll(request.URL.Path, "/", "")+".json"
            //fmt.Println(filename)
            //See how old My Config is
            filestat, _ := os.Stat(filename)
            file, _ := ioutil.ReadFile(filename)
            json.Unmarshal(file, &config)
            config.Time=filestat.ModTime().Unix()
            fmt.Println(config)
            rw.Header().Set("Content-Type", "application/json")
            json.NewEncoder(rw).Encode(config)
            fmt.Printf("--------COMPLETE SERVING OF LM CONFIG --------\n")

      case "POST":
            //Keep a List of All LMs we know about - e.g. lmnow[id]
            //Extract LMID
            //lmbefore becomes lmnow[id]
            fmt.Printf("--------POST of LM Stats--------\n")

            custid := strings.ReplaceAll(strings.Split(request.URL.Path, "_")[0],"/", "")
            fmt.Printf(custid)

            lmbefore=lmnow
            lmnow= LoadMaster{}

            //find LMbefore from list of all LMs by ID, that matches this one

	        decoder := json.NewDecoder(request.Body)

	        err := decoder.Decode(&lmnow)

	        fmt.Printf("%+v\n",lmnow)
	        if err != nil {
		        panic(err)
	        }

            //Write Data to Influx
            //Pass in LoadMaster Object
            writeToInflux(lmnow)



	        vsupdownrule(lmnow,lmbefore,custid)
	        rsupdownrule(lmnow,lmbefore,custid)

            //fmt.Println(lmnow)
            //fmt.Println(lmbefore)
            fmt.Printf("--------COMPLETE PROCESSING POST of LM Stats--------\n")
      default:
    }

}


func main() {

    // Pass in Options to Write Stats to Influx, File to Write Issues to
    custid := os.Args[1]
	http.HandleFunc("/", parseGhPost)
	http.ListenAndServe(":"+custid, nil)
}