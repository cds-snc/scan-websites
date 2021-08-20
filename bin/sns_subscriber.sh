#!/bin/bash

while true; do {
  echo -e 'HTTP/1.1 200 OK\r\n\r\n';  
} | netcat -l -p 8081
done