OPENQASM 3.0;
include "stdgates.inc";

// Teleports the state of q[0] to q[2].
// The corrections on q[2] depend on mid-circuit measurements,
// so this kernel needs feed-forward on the device (tier: realtime).

qubit[3] q;
bit[2] m;
bit result;

// state to teleport
ry(0.7) q[0];

// Bell pair between q[1] and q[2]
h q[1];
cx q[1], q[2];

// Bell measurement of q[0] and q[1]
cx q[0], q[1];
h q[0];
m[0] = measure q[0];
m[1] = measure q[1];

// real-time corrections
if (m[1]) x q[2];
if (m[0]) z q[2];

result = measure q[2];
