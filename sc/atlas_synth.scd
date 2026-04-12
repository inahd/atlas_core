/*
  atlas_synth.scd — SC audio engine for Atlas

  Connects to externally-booted scsynth (via pw-jack).
  Loads SynthDefs, receives OSC from Python.
  Python handles NPU + field state. SC handles all sound.

  Replaces: om_audio.py, om.py audio path, atlas_mix.scd

  Start:
    PIPEWIRE_LATENCY=512/48000 pw-jack scsynth -u 57110 -o 2 -R 0 -l 1 &
    sclang ~/atlas_330/sc/atlas_synth.scd

  SynthDefs:
    \tanpura_engine  — four physical strings, staggered pluck
    \raga_note       — melodic note with gamaka
    \tabla_bol       — tabla stroke synthesis
    \bija_drone      — formant bija mantra
    \master          — reverb + limiter on master bus

  OSC routes (port 57120):
    /atlas/tanpura/sa      [sa_hz]
    /atlas/tanpura/jivari  [jivari]
    /atlas/tanpura/amp     [scale]
    /atlas/note            [freq amp dur gamaka gamaka_rate gamaka_depth]
    /atlas/tabla           [bol_idx amp]
    /atlas/bija            [freq f1 f2 f3 amp]
    /atlas/master          [reverb decay amp]
    /atlas/field           [sa jivari guna_idx elem_idx]
*/

// Connect to scsynth booted externally via pw-jack:
//   PIPEWIRE_LATENCY=512/48000 pw-jack scsynth -u 57110 -o 2 -R 0 -l 1 &
//
// sclang sends SynthDefs + OSC to the running server.

s = Server(\atlas, NetAddr("127.0.0.1", 57110));
Server.default = s;
s.options.sampleRate = 48000;
s.options.numBuffers = 1024;
s.options.memSize = 65536;

// Connect to scsynth via UDP and load SynthDefs
fork {
    "Waiting for scsynth on 127.0.0.1:57110...".postln;

    // Ping until scsynth responds
    10.do {
        s.sendStatusMsg;
        0.3.wait;
    };

    // Register for notifications (replies to Synth/Buffer creation)
    s.notify;
    1.0.wait;
    s.sync;
    "scsynth connected.".postln;

// ======================================================
// SYNTHDEF 1 — TANPURA ENGINE
// Four strings. Staggered plucking. Jivari buzz.
// ======================================================

SynthDef(\tanpura_engine, {
    |out=0, sa=130.81,
     amp_pa=0.22, amp_sa1=0.30,
     amp_sa2=0.28, amp_salow=0.20,
     jivari=0.40, gate=1|

    var pa, sa1, sa2, sa_low;
    var mix, cycle, excite_pa, excite_sa1, excite_sa2, excite_salow;

    // Cycle impulse — 7 second cycle, staggered phases
    cycle = 1/7.0;

    // Pluck excitations — filtered noise bursts
    excite_pa = PinkNoise.ar(0.2) *
        EnvGen.ar(Env.perc(0.001, 0.04), Impulse.ar(cycle, 0.0));
    excite_sa1 = PinkNoise.ar(0.2) *
        EnvGen.ar(Env.perc(0.001, 0.04), Impulse.ar(cycle, 0.143));
    excite_sa2 = PinkNoise.ar(0.2) *
        EnvGen.ar(Env.perc(0.001, 0.04), Impulse.ar(cycle, 0.286));
    excite_salow = PinkNoise.ar(0.2) *
        EnvGen.ar(Env.perc(0.001, 0.04), Impulse.ar(cycle, 0.429));

    // Pa string — fundamental + overtones
    pa = CombL.ar(excite_pa, 1/20.0, 1/(sa*1.5), 8.0)
       + CombL.ar(excite_pa, 1/20.0, 1/(sa*3.0), 5.6) * 0.3
       + CombL.ar(excite_pa, 1/20.0, 1/(sa*4.5), 4.0) * 0.15;

    // Sa string 1 — fundamental + overtones
    sa1 = CombL.ar(excite_sa1, 1/20.0, 1/sa, 10.0)
        + CombL.ar(excite_sa1, 1/20.0, 1/(sa*2), 7.0) * 0.3
        + CombL.ar(excite_sa1, 1/20.0, 1/(sa*3), 5.0) * 0.15;

    // Sa string 2 — slight detune (3.5 cents)
    sa2 = CombL.ar(excite_sa2, 1/20.0, 1/(sa*1.002), 10.0)
        + CombL.ar(excite_sa2, 1/20.0, 1/(sa*2.004), 7.0) * 0.3
        + CombL.ar(excite_sa2, 1/20.0, 1/(sa*3.006), 5.0) * 0.15;

    // Sa low — octave below + overtones
    sa_low = CombL.ar(excite_salow, 1/20.0, 1/(sa*0.5), 12.0)
           + CombL.ar(excite_salow, 1/20.0, 1/sa, 8.4) * 0.3
           + CombL.ar(excite_salow, 1/20.0, 1/(sa*1.5), 6.0) * 0.15;

    // Jivari — start minimal, no instability
    pa     = pa     * 0.8;
    sa1    = sa1    * 0.8;
    sa2    = sa2    * 0.8;
    sa_low = sa_low * 0.8;

    // No waveshaping yet.
    // Get the clean string tone first.
    // Add jivari back once stable.

    // Mix with per-string levels
    mix = (pa * amp_pa) + (sa1 * amp_sa1) + (sa2 * amp_sa2) + (sa_low * amp_salow);

    // Gentle reverb — gourd resonance
    mix = mix + FreeVerb.ar(mix, 0.15, 0.3, 0.4);

    mix = mix * EnvGen.ar(Env.asr(3.0, 1.0, 3.0), gate, doneAction: 2);
    mix = Limiter.ar(mix, 0.6);
    Out.ar(out, mix * 0.7 ! 2);

}).store;

// ======================================================
// SYNTHDEF 2 — SINGLE TANPURA STRING
// For future per-string control if needed
// ======================================================

SynthDef(\tanpura_string, {
    |out=0, freq=130.81, amp=0.3,
     jivari=0.4, decay=10.0, gate=1|

    var excite, string, jiv, env;

    excite = PinkNoise.ar(0.3) *
        EnvGen.ar(Env.perc(0.001, 0.05), Impulse.ar(1/decay));

    // Fundamental + overtones
    string = CombL.ar(excite, 1/20.0, 1/freq, decay)
           + CombL.ar(excite, 1/20.0, 1/(freq*2), decay*0.7) * 0.3
           + CombL.ar(excite, 1/20.0, 1/(freq*3), decay*0.5) * 0.15
           + CombL.ar(excite, 1/20.0, 1/(freq*4), decay*0.3) * 0.08;

    // Jivari
    jiv = (string * (1 + (jivari * 8))).tanh / (1 + (jivari * 8));
    string = (string * (1 - jivari)) + (jiv * jivari);

    env = EnvGen.ar(Env.asr(2.0, 1.0, 2.0), gate, doneAction: 2);

    Out.ar(out, string * amp * env ! 2);

}).store;

// ======================================================
// SYNTHDEF 3 — MELODIC NOTE
// One note with gamaka modulation.
// ======================================================

SynthDef(\raga_note, {
    |out=0, freq=261.63, amp=0.4,
     dur=1.0, gamaka=0, gamaka_rate=5,
     gamaka_depth=0.015|

    var sig, env, freq_mod;

    // Gamaka types: 0=none 1=kampita 2=andolan 3=meend
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        // kampita — fast oscillation
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        // andolan — slow wave
        freq * (1 + SinOsc.ar(gamaka_rate * 0.4, 0, gamaka_depth * 0.6)),
        // meend — exponential approach
        freq * (1 + XLine.ar(0.05, 0.001, dur * 0.3)),
    ]);

    // Plucked string timbre
    sig = Pluck.ar(
        WhiteNoise.ar(0.3),
        Impulse.ar(0),
        1/20.0,
        1/freq_mod,
        dur * 2,
        0.25
    );

    // Slight breath quality
    sig = sig + (SinOsc.ar(freq_mod, 0, 0.1) *
        EnvGen.ar(Env.perc(0.01, dur * 0.8)));

    env = EnvGen.ar(
        Env.new([0, 1, 0.7, 0], [0.005, dur * 0.7, dur * 0.25]),
        doneAction: 2
    );

    Out.ar(out, sig * amp * env ! 2);

}).store;

// ======================================================
// SYNTHDEF 4 — TABLA BAYAN (bass drum, left hand)
// Pitch-envelope membrane synthesis
// ======================================================

SynthDef(\tabla_bayan, {
    |out=0, freq=110, endFreq=55, decay=0.25,
     amp=0.5, resonance=0.3|

    var membrane, overtone, strike, env, sig;

    // Membrane — fast pitch drop
    membrane = SinOsc.ar(
        XLine.ar(freq, endFreq, decay * 0.6),
        0, 0.8
    );

    // Overtone — adds body
    overtone = SinOsc.ar(
        XLine.ar(freq * 1.5, endFreq * 1.3, decay * 0.4),
        0, 0.2
    );

    // Strike transient
    strike = WhiteNoise.ar(0.4) *
        EnvGen.ar(Env.perc(0.001, 0.04));

    env = EnvGen.ar(Env.perc(0.001, decay), doneAction: 2);

    sig = (membrane + overtone + strike) * env;
    sig = LPF.ar(sig, 400);
    sig = sig + (FreeVerb.ar(sig, resonance, 0.2, 0.3) * 0.15);

    Out.ar(out, sig * amp ! 2);
}).store;

// ======================================================
// SYNTHDEF 4b — TABLA DAYAN (treble drum, right hand)
// Resonant membrane with overtone series
// ======================================================

SynthDef(\tabla_dayan, {
    |out=0, freq=440, decay=0.12, amp=0.4,
     brightness=0.5, mute=0|

    var membrane, overtones, strike, env, sig;

    // Fundamental membrane
    membrane = SinOsc.ar(freq, 0, 0.6);

    // Overtone series — characteristic tabla ring
    overtones = SinOsc.ar(freq * 2.14, 0, 0.2)  // syahi overtone
              + SinOsc.ar(freq * 3.01, 0, 0.1)
              + SinOsc.ar(freq * 4.16, 0, 0.05 * brightness);

    // Strike
    strike = HPF.ar(
        WhiteNoise.ar(0.3) *
        EnvGen.ar(Env.perc(0.001, 0.03)),
        800
    );

    // Muting: shorter decay + less overtones
    env = EnvGen.ar(
        Env.perc(0.001, decay * (1 - (mute * 0.6))),
        doneAction: 2
    );

    sig = (membrane + overtones + strike) * env;
    sig = HPF.ar(sig, 200); // remove bass bleed

    Out.ar(out, sig * amp ! 2);
}).store;

// ======================================================
// SYNTHDEF 4c — TABLA BOL (composite — selects bol by index)
// 0=Dha 1=Dhin 2=Na 3=Ka 4=Ti 5=Ge 6=Ta
// ======================================================

SynthDef(\tabla_bol, {
    |out=0, bol=0, amp=0.5|

    var bayan, dayan, strike, sig, env;
    var bayAmp, dayAmp, bayFreq, dayFreq, dayDecay, dayMute;

    // Bol parameters: [bayAmp, dayAmp, bayFreq, dayFreq, dayDecay, dayMute]
    // Dha:  full bayan + open dayan
    // Dhin: no bayan + resonant long dayan
    // Na:   no bayan + muted short dayan
    // Ka:   bayan only (pitch drop)
    // Ti:   no bayan + high short dayan
    // Ge:   open bayan (longer, resonant)
    // Ta:   muted dayan + noise

    bayAmp   = Select.kr(bol, [0.7,  0.0,  0.0,  0.8,  0.0,  0.6,  0.0]);
    dayAmp   = Select.kr(bol, [0.5,  0.7,  0.5,  0.0,  0.6,  0.0,  0.5]);
    bayFreq  = Select.kr(bol, [110,  110,  110,  100,  110,  90,   110]);
    dayFreq  = Select.kr(bol, [440,  380,  520,  440,  550,  440,  500]);
    dayDecay = Select.kr(bol, [0.12, 0.20, 0.08, 0.12, 0.06, 0.12, 0.06]);
    dayMute  = Select.kr(bol, [0,    0,    0.7,  0,    0,    0,    0.8]);

    // Bayan
    bayan = SinOsc.ar(
        XLine.ar(bayFreq, bayFreq * 0.5, 0.15), 0, 0.8
    ) * EnvGen.ar(Env.perc(0.001, 0.25));

    // Dayan
    dayan = SinOsc.ar(dayFreq, 0, 0.6)
          + SinOsc.ar(dayFreq * 2.14, 0, 0.15)
          + SinOsc.ar(dayFreq * 3.01, 0, 0.05);
    dayan = dayan * EnvGen.ar(Env.perc(0.001, dayDecay * (1 - (dayMute * 0.5))));
    dayan = HPF.ar(dayan, 200);

    // Strike noise
    strike = WhiteNoise.ar(0.3) * EnvGen.ar(Env.perc(0.001, 0.04));

    sig = (bayan * bayAmp) + (dayan * dayAmp) + (strike * 0.3);
    env = EnvGen.ar(Env.perc(0.001, 0.35), doneAction: 2);

    Out.ar(out, sig * amp * env ! 2);
}).store;

// ======================================================
// SYNTHDEF 5 — SANTOOR NOTE
// 100-string hammered dulcimer — 4 detuned strings per course
// Characteristic shimmer from beating frequencies
// ======================================================

SynthDef(\santoor_note, {
    |out=0, freq=440, amp=0.4,
     dur=1.0, pan=0, shimmer=0.003|

    var s1, s2, s3, s4, strings, strike, env, sig;

    // 4 strings per course — slight detuning creates santoor shimmer
    s1 = CombL.ar(WhiteNoise.ar(0.08), 0.05, freq.reciprocal, dur * 3.5);
    s2 = CombL.ar(WhiteNoise.ar(0.08), 0.05, (freq * (1 + shimmer)).reciprocal, dur * 3.5);
    s3 = CombL.ar(WhiteNoise.ar(0.08), 0.05, (freq * (1 - shimmer)).reciprocal, dur * 3.5);
    s4 = CombL.ar(WhiteNoise.ar(0.08), 0.05, (freq * (1 + (shimmer * 0.7))).reciprocal, dur * 3.5);
    strings = (s1 + s2 + s3 + s4) * 0.25;

    // Mallet strike transient
    strike = WhiteNoise.ar(0.15) *
        EnvGen.ar(Env.perc(0.001, 0.012));

    // Natural hammered dulcimer envelope
    env = EnvGen.ar(
        Env.new([0, 1, 0.3, 0], [0.002, 0.05, dur]),
        doneAction: 2
    );

    sig = (strings + strike) * env * amp;
    Out.ar(out, Pan2.ar(sig, pan));

}).store;

// ======================================================
// SYNTHDEF 6 — BIJA DRONE
// Formant synthesis from bija vowel.
// ======================================================

SynthDef(\bija_drone, {
    |out=0, freq=130.81, amp=0.08,
     f1=800, f2=1200, f3=2500, gate=1|

    var src, sig, env;

    // Voiced source
    src = Saw.ar(freq, 0.3) + Saw.ar(freq * 1.007, 0.2);

    // Three formants
    sig = (BPF.ar(src, f1, 0.3) * 1.5) +
          (BPF.ar(src, f2, 0.2) * 1.0) +
          (BPF.ar(src, f3, 0.15) * 0.5);

    env = EnvGen.ar(Env.asr(4.0, 1.0, 4.0), gate, doneAction: 2);

    Out.ar(out, sig * amp * env ! 2);

}).store;

// ======================================================
// SYNTHDEF 6 — MASTER BUS
// Reverb + soft limiting. Never clips.
// ======================================================

SynthDef(\master, {
    |out=0, in=0, reverb=0.15,
     decay=1.2, amp=0.75|

    var sig, wet;

    sig = In.ar(in, 2);

    wet = FreeVerb2.ar(sig[0], sig[1], reverb, 0.4, decay);
    sig = (sig * (1 - reverb)) + (wet * reverb);

    // Soft limiter
    sig = Limiter.ar(sig, 0.85, 0.01);

    Out.ar(out, sig * amp);

}).store;

// ======================================================
// SYNTH INSTANCES
// ======================================================

"SynthDefs stored — waiting for scsynth to load...".postln;
3.0.wait;

// Initialize the default group (Group 1) on the remote server
s.initTree;
0.5.wait;
s.sync;

// Start tanpura — direct to hardware out 0
~tanpura = Synth(\tanpura_engine, [
    \out, 0,
    \sa, 130.81,
    \jivari, 0.40,
    \amp_pa, 0.22,
    \amp_sa1, 0.30,
    \amp_sa2, 0.28,
    \amp_salow, 0.20,
]);

// Start bija drone — direct to hardware out 0
~bija = Synth(\bija_drone, [
    \out, 0,
    \freq, 130.81,
    \amp, 0.06,
    \f1, 800,
    \f2, 1200,
    \f3, 2500,
]);

"".postln;
"======================================================".postln;
"  Atlas synth engine running (direct out)".postln;
"  tanpura: Sa=130.81Hz jivari=0.40".postln;
"  bija: krim drone".postln;
"======================================================".postln;

// ======================================================
// OSC RECEIVERS — Python sends here
// ======================================================

~atlasPort = 57120;

// /atlas/tanpura/sa — update Sa frequency
OSCFunc({ |msg|
    var sa = msg[1];
    ~tanpura.set(\sa, sa);
    ~bija.set(\freq, sa);
    "tanpura Sa -> %Hz".format(sa).postln;
}, '/atlas/tanpura/sa');

// /atlas/tanpura/jivari — update buzz
OSCFunc({ |msg|
    ~tanpura.set(\jivari, msg[1]);
}, '/atlas/tanpura/jivari');

// /atlas/tanpura/amp — scale all string levels
OSCFunc({ |msg|
    var scale = msg[1];
    ~tanpura.set(
        \amp_pa,    scale * 0.22,
        \amp_sa1,   scale * 0.30,
        \amp_sa2,   scale * 0.28,
        \amp_salow, scale * 0.20
    );
}, '/atlas/tanpura/amp');

// /atlas/note — play a melodic note
OSCFunc({ |msg|
    Synth(\raga_note, [
        \out,           0,
        \freq,          msg[1] ? 261.63,
        \amp,           msg[2] ? 0.4,
        \dur,           msg[3] ? 1.0,
        \gamaka,        msg[4] ? 0,
        \gamaka_rate,   msg[5] ? 5,
        \gamaka_depth,  msg[6] ? 0.015,
    ]);
}, '/atlas/note');

// /atlas/tabla — play a tabla bol
OSCFunc({ |msg|
    Synth(\tabla_bol, [
        \out, 0,
        \bol, msg[1] ? 0,
        \amp, msg[2] ? 0.5,
    ]);
}, '/atlas/tabla');

// /atlas/bija — update bija formants
OSCFunc({ |msg|
    ~bija.set(
        \freq, msg[1] ? 130.81,
        \f1,   msg[2] ? 800,
        \f2,   msg[3] ? 1200,
        \f3,   msg[4] ? 2500,
        \amp,  msg[5] ? 0.06
    );
}, '/atlas/bija');

// /atlas/master — global volume (no master bus, scale tanpura + bija)
OSCFunc({ |msg|
    var amp = msg[3] ? 0.75;
    ~tanpura.set(
        \amp_pa,    amp * 0.22,
        \amp_sa1,   amp * 0.30,
        \amp_sa2,   amp * 0.28,
        \amp_salow, amp * 0.20
    );
    ~bija.set(\amp, amp * 0.08);
}, '/atlas/master');

// /atlas/field — full field update from Python
OSCFunc({ |msg|
    var sa       = msg[1] ? 130.81;
    var jivari   = msg[2] ? 0.40;
    var guna_idx = msg[3] ? 1;
    var elem_idx = msg[4] ? 4;

    ~tanpura.set(\sa, sa, \jivari, jivari);
    ~bija.set(\freq, sa);

    "field: Sa=% jivari=% guna=% elem=%"
        .format(sa, jivari, guna_idx, elem_idx).postln;
}, '/atlas/field');

// /atlas/mix/layers — from MixKernel (11 floats)
// Forward-compatible: store for future per-layer SC control
OSCFunc({ |msg|
    ~layerAmps = msg[1..11];
}, '/atlas/mix/layers');

// /atlas/mix/global — brightness, reverb from MixKernel
// (reverb is internal to tanpura_engine SynthDef — stored for future use)
OSCFunc({ |msg|
    ~mixBrightness = msg[1] ? 0.0;
    ~mixReverb = msg[2] ? 0.15;
}, '/atlas/mix/global');

// ======================================================
// SANTOOR OSC — receives note events from Python
// ======================================================

// /atlas/santoor/note [freq, amp, dur, pan]
OSCFunc({ |msg|
    Synth(\santoor_note, [
        \out,     0,
        \freq,    msg[1] ? 440,
        \amp,     msg[2] ? 0.35,
        \dur,     msg[3] ? 0.8,
        \pan,     msg[4] ? 0,
        \shimmer, 0.003,
    ]);
}, '/atlas/santoor/note');

OSCFunc({ |msg|
    "Santoor: melodic layer active".postln;
}, '/atlas/santoor/start');

OSCFunc({ |msg|
    "Santoor: melodic layer stopped".postln;
}, '/atlas/santoor/stop');

// ======================================================
// TABLA THEKA ROUTINES
// ======================================================

// Bol indices: 0=Dha 1=Dhin 2=Na 3=Ka 4=Ti 5=Ge 6=Ta
~tablaRunning = false;
~tablaBPM = 84;

// Thekas (bol sequences with beat fractions)
~thekas = (
    rupak: #[0, 1, 2, 0, 4, 2, 2],  // Dha Dhin Na | Dha Ti Na | Na  (7 beats)
    teental: #[0, 0, 1, 0, 0, 0, 1, 0, 0, 6, 1, 0, 0, 0, 1, 0],  // 16 beats
    dadra: #[0, 0, 2, 6, 0, 2],  // Dha Dha Na | Ge Dha Na  (6 beats)
    jhaptal: #[0, 1, 0, 1, 2, 6, 4, 1, 0, 2],  // 10 beats
);

~tablaRoutine = nil;

~playTheka = { |thekaName=\rupak, bpm=84, amp=0.4|
    var theka = ~thekas[thekaName] ?? ~thekas[\rupak];
    var beatDur = 60.0 / bpm;

    ~tablaRunning = true;
    ~tablaBPM = bpm;
    ~tablaRoutine.stop;
    ~tablaRoutine = Routine({
        "Tabla: % at %bpm".format(thekaName, bpm).postln;
        loop {
            theka.do { |bol|
                if(~tablaRunning) {
                    Synth(\tabla_bol, [\out, 0, \bol, bol, \amp, amp]);
                    beatDur.wait;
                } {
                    nil.yield; // stop
                };
            };
        };
    }).play(TempoClock.default);
};

~stopTheka = {
    ~tablaRunning = false;
    ~tablaRoutine.stop;
    "Tabla stopped.".postln;
};

// /atlas/tabla/start [bpm, theka_idx, amp]
// theka_idx: 0=rupak 1=teental 2=dadra 3=jhaptal
OSCFunc({ |msg|
    var bpm = msg[1] ? 84;
    var thekaIdx = msg[2] ? 0;
    var amp = msg[3] ? 0.4;
    var thekaNames = #[\rupak, \teental, \dadra, \jhaptal];
    var thekaName = thekaNames[thekaIdx.asInteger.clip(0, 3)];
    ~playTheka.(thekaName, bpm, amp);
    "tabla/start: % at %bpm amp=%".format(thekaName, bpm, amp).postln;
}, '/atlas/tabla/start');

// /atlas/tabla/stop
OSCFunc({ |msg|
    ~stopTheka.();
}, '/atlas/tabla/stop');

// ======================================================
// JACK CONNECTIONS — connect SC outputs to MOTU M2
// Done here (after synths run) so PipeWire/WirePlumber
// doesn't drop early connections from start_sc.sh
// ======================================================

"Connecting JACK → MOTU M2...".postln;
"pw-jack jack_connect SuperCollider:out_1 'M Series Analog Stereo:playback_FL'".systemCmd;
"pw-jack jack_connect SuperCollider:out_2 'M Series Analog Stereo:playback_FR'".systemCmd;
0.5.wait;
"JACK connected.".postln;

"".postln;
"  OSC listening on port %".format(~atlasPort).postln;
"  /atlas/tanpura/sa     set Sa frequency".postln;
"  /atlas/tanpura/jivari set buzz".postln;
"  /atlas/note           play melodic note".postln;
"  /atlas/tabla          play single bol (0-6)".postln;
"  /atlas/tabla/start    start theka [bpm, theka, amp]".postln;
"  /atlas/tabla/stop     stop theka".postln;
"  /atlas/bija           update bija drone".postln;
"  /atlas/master         global mix".postln;
"  /atlas/field          full field update".postln;
"".postln;

}; // end fork

// Keep sclang alive
Routine({ loop { 1.0.wait } }).play(AppClock);
