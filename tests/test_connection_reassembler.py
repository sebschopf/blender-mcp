from blender_mcp.services.connection.reassembler import ChunkedJSONReassembler


def test_reassembler_basic_flow():
    r = ChunkedJSONReassembler()
    # feed two JSON objects separated by newline
    r.feed(b'{"a":1}\n')
    msgs = r.pop_messages()
    assert msgs == [{"a": 1}]

    # feed partial then remainder
    r.feed(b'{"b":')
    r.feed(b'2}\n')
    msgs = r.pop_messages()
    assert msgs == [{"b": 2}]
