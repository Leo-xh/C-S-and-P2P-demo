# Implementation Notes on Peer

## Constraint (temporarily)
- ignore the peer states
- peer id used as a unique key for a peer, a collision with active peers' ids or own id is unacceptable
- AT MOST one `Request` is sent for a missing piece
    - the cap on the size of any request list is 1
    - no `Cancel` is needed

## Strategy
- piece selection
    - rarest-first order
- peer selection
    - random

## Mechanism
- peer list, active peer list
    - peer list is the list received from tracker
    - active peer list is the list of connected peers
    - active peer list records:
        - the bitfields of the peers
        - the time of last message sent / received ?
    - there is a cap on the number of active peers
- request list
    - each piece has a request list, which records the peers that we will send `Request` to
    - there is a cap on the size of a request list
    - there is a cap on the total size of all request lists
    - a global counter (request count) is maintained
- piece list
    - for each piece, records:
        - have/not have this piece
        - request list
        - the state of each block
        - the received data
    - a block state can be:
        - `Request` not sent
        - `Request` sent, not received
        - received

## Events and Reactions for a Peer

### New Connection and Handshaking
- every few seconds
    - try connecting a not yet connected peer (if possible)
- receive a handshake
    - check the protocol name, info hash and peer id
        - valid: reply a handshake, add to active peer list
        - invalid: abort connection
- receive a reply of handshake
    - check peer id
        - valid: send `Bitfield`, add to active peer list
        - invalid: abort connection
- receive a `Bitfield`
    - update the bitfield of this peer
    - if have not sent a `Bitfield` to this peer before, send one

### Keeping and Ending Connection
- every few seconds
    - send keep-alive messages to active peers IF NEEDED
- every few minutes
    - abort connections to dead peers
- connection lost
    - remove the peer from active peer list
    - remove the peer from all request lists, update the request count

### Data
- every few seconds
    - check if request count is under cap
        - yes: 
            1. select a missing piece that is able to make more requests
            2. select a peer that has this piece and not in the request list (if none exists, repeat 1.)
            3. add the peer to peer list
            4. update request count
- every few seconds
    1. select a piece with nonempty request list and a block in the state of `Request` not sent
    2. select a peer in the request list
    3. send `Request`
    4. update the block state
- receive a `Request`
    - send `Piece`
- receive a `Piece`
    1. cache the block (in memory)
    2. update the block state 
    3. check whether the piece downloading is finished
- finish downloading a piece
    - validate the piece
        - valid: write to file, update the piece state, send `Have` to all of its peers, check if the download finishes, update bitfield
        - invalid: remove the peer from the request list of this piece, reset the block states
    - update the request count
- finish downloading the file
    - print message
- receive a `Have`
    - update the bitfield of this peer

### bitField Recordpytp

a number whose number of bits is larger than number of pieces.
