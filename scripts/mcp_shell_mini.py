#!/usr/bin/env python3
"""Minimal MCP Shell Server for Chatbox"""

import json
import subprocess
import sys

def read_message():
    line = sys.stdin.readline()
    if not line:
        return None
    line = line.strip()
    return json.loads(line)

def send_response(response):
    data = json.dumps(response)
    sys.stdout.write(f'Content-Length: {len(data.encode("utf-8"))}\r\n\r\n{data}')
    sys.stdout.flush()

def main():
    while True:
        msg = read_message()
        if msg is None:
            break
        method = msg.get('method', '')
        req_id = msg.get('id', 0)
        
        if method == 'initialize':
            send_response({
                'jsonrpc': '2.0', 'id': req_id,
                'result': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {'tools': {}},
                    'serverInfo': {'name': 'mcp-shell-mini', 'version': '1.0.0'}
                }
            })
        elif method == 'tools/list':
            send_response({
                'jsonrpc': '2.0', 'id': req_id,
                'result': {
                    'tools': [{
                        'name': 'run_command',
                        'description': 'Execute a shell command. Returns stdout/stderr/exit code. Timeout: 120s.',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'command': {'type': 'string', 'description': 'Shell command to execute'},
                                'cwd': {'type': 'string', 'description': 'Working directory (optional)'}
                            },
                            'required': ['command']
                        }
                    }]
                }
            })
        elif method == 'tools/call':
            params = msg.get('params', {})
            tool_name = params.get('name', '')
            args = params.get('arguments', {})
            
            if tool_name == 'run_command':
                cmd = args.get('command', '')
                cwd = args.get('cwd', None)
                try:
                    result = subprocess.run(
                        cmd, shell=True, capture_output=True, text=True,
                        timeout=120, cwd=cwd
                    )
                    output = f'STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nEXIT: {result.returncode}'
                except subprocess.TimeoutExpired:
                    output = 'ERROR: Command timed out (120s)'
                except Exception as e:
                    output = f'ERROR: {str(e)}'
                send_response({
                    'jsonrpc': '2.0', 'id': req_id,
                    'result': {'content': [{'type': 'text', 'text': output}]}
                })
            else:
                send_response({
                    'jsonrpc': '2.0', 'id': req_id,
                    'error': {'code': -32601, 'message': f'Unknown tool: {tool_name}'}
                })
        elif method == 'notifications/initialized':
            pass
        else:
            send_response({
                'jsonrpc': '2.0', 'id': req_id,
                'error': {'code': -32601, 'message': f'Unknown method: {method}'}
            })

if __name__ == '__main__':
    main()
