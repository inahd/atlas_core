/*
  atlas_mix.scd — Pure OSC receiver for npu_engine/mix/
  No scsynth, no JACK, no audio hardware.

  Receives from MixKernel on port 57121.
  Echoes /atlas/mix/layers + /atlas/mix/global back to om.py on port 57122
  so om.py can scale tanpura/tabla amps directly.

  Run: sclang ~/atlas_330/sc/atlas_mix.scd

  LAYERS (positional in /atlas/mix/layers):
    [0]  tanpura       [1]  mantra_drone  [2]  vocal_pad
    [3]  tabla         [4]  konnakol      [5]  bol
    [6]  melody        [7]  vocal_line    [8]  pad
    [9]  electronic    [10] bija
*/

~atlasPort  = 57121;   // receive from MixKernel
~omPort     = 57122;   // echo back to om.py
~omAddr     = NetAddr("127.0.0.1", ~omPort);

~layerNames = [\tanpura, \mantra_drone, \vocal_pad,
               \tabla, \konnakol, \bol,
               \melody, \vocal_line,
               \pad, \electronic, \bija];

~layerAmps   = Array.fill(11, { 1.0 });
~brightness  = 0.0;
~reverbDepth = 0.15;
~reverbDecay = 1.2;
~sub         = 0.0;
~compression = 0.0;
~stereoWidth = 0.5;
~confidence  = 0.6;

// ── OSC responders
if(~atlasOSCResponders.notNil, { ~atlasOSCResponders.do(_.free) });
~atlasOSCResponders = [];

// /atlas/mix/layers — store state + echo to om.py
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        var amps = msg[1..11];
        amps.do { |amp, i| ~layerAmps[i] = amp.clip(0, 1) };
        "mix: received /layers — tanpura=% tabla=% bija=%".format(
            ~layerAmps[0].round(0.01),
            ~layerAmps[3].round(0.01),
            ~layerAmps[10].round(0.01)
        ).postln;
        // Echo to om.py so it can scale audio buffers
        ~omAddr.sendMsg('/atlas/mix/layers', *~layerAmps);
        "mix: echoed to om.py on 57122".postln;
    }, '/atlas/mix/layers', recvPort: ~atlasPort)
);

// /atlas/mix/global — store + echo brightness and reverb
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        ~brightness  = (msg[1] ? 0.0).clip(-0.3, 0.3);
        ~reverbDepth = (msg[2] ? 0.15).clip(0, 0.9);
        ~reverbDecay = (1.2 + ((msg[3] ? 0.0) * 7)).clip(0.5, 8.0);
        ~sub         = (msg[4] ? 0.0).clip(0, 0.5);
        ~compression = (msg[5] ? 0.0).clip(0, 1);
        "mix: received /global — brightness=% reverb=%".format(
            ~brightness.round(0.01), ~reverbDepth.round(0.01)
        ).postln;
        // Echo brightness + reverb to om.py
        ~omAddr.sendMsg('/atlas/mix/global', ~brightness, ~reverbDepth);
    }, '/atlas/mix/global', recvPort: ~atlasPort)
);

// /atlas/mix/spatial
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        ~stereoWidth  = (msg[1] ? 0.5).clip(0, 1);
        ~centerWeight = (msg[2] ? 0.5).clip(0, 1);
    }, '/atlas/mix/spatial', recvPort: ~atlasPort)
);

// /atlas/mix/confidence
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        ~confidence = (msg[1] ? 0.6).clip(0, 1);
    }, '/atlas/mix/confidence', recvPort: ~atlasPort)
);

// /atlas/mix/sam_event — immediate convergence, echo to om.py
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        ~omAddr.sendMsg('/atlas/mix/sam_event');
        "✦ sam — %".format(
            ~layerNames.collect { |n, i|
                "%(%)".format(n, ~layerAmps[i].round(0.01))
            }
        ).postln;
    }, '/atlas/mix/sam_event', recvPort: ~atlasPort)
);

// /atlas/mix/khali_event
~atlasOSCResponders = ~atlasOSCResponders.add(
    OSCFunc({ |msg|
        ~omAddr.sendMsg('/atlas/mix/khali_event');
        "✦ khali".postln;
    }, '/atlas/mix/khali_event', recvPort: ~atlasPort)
);

"✦ Atlas mix OSC ready".postln;
"  recv  127.0.0.1:%".format(~atlasPort).postln;
"  echo  127.0.0.1:%".format(~omPort).postln;
"✦ /layers | /global | /spatial | /confidence | /sam_event | /khali_event".postln;

// Keep sclang alive
Routine({ loop { 1.0.wait } }).play(AppClock);
