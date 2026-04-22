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
    \tanpura_string  — single string (per-string control)
    \raga_note       — melodic note with gamaka
    \raga_phrase     — continuous pitch envelope
    \tabla_bayan     — bass drum membrane
    \tabla_dayan     — treble drum membrane
    \tabla_bol       — composite tabla stroke (7 bols)
    \santoor_note    — hammered dulcimer shimmer
    \sarangi_note    — bowed gut string (the voice)
    \mridangam_bol   — Carnatic barrel drum (7 bols)
    \pakhawaj_bol    — Dhrupad barrel drum (7 bols)
    \bansuri_note    — bamboo flute (breathy, pure)
    \sitar_note      — plucked with jawari buzz + taraf
    \shehnai_note    — double reed (festive, temple)
    \bija_drone      — formant bija mantra
    \master          — reverb + limiter on master bus

  OSC routes (port 57120):
    /atlas/tanpura/sa      [sa_hz]
    /atlas/tanpura/jivari  [jivari]
    /atlas/tanpura/amp     [scale]
    /atlas/note            [freq amp dur gamaka gamaka_rate gamaka_depth]
    /atlas/phrase          [freq1..3 dur1..3 gamak_rate depth note amp pan]
    /atlas/tabla           [bol_idx amp]
    /atlas/santoor/note    [freq amp dur pan]
    /atlas/sarangi/note    [freq amp dur bow gamaka rate depth pan]
    /atlas/mridangam       [bol_idx amp freq]
    /atlas/pakhawaj        [bol_idx amp freq]
    /atlas/bansuri/note    [freq amp dur breath gamaka rate depth pan]
    /atlas/sitar/note      [freq amp dur jawari gamaka rate depth pan]
    /atlas/shehnai/note    [freq amp dur reed gamaka rate depth pan]
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
     amp_ga=0.0, amp_ma=0.0,
     drift=0, jivari=0.40, gate=1|

    var pa, sa1, sa2, sa_low, ga_str, ma_str;
    var mix, cycle, excite_pa, excite_sa1, excite_sa2, excite_salow;

    // ── Breath: 4-second prana cycle, depth controlled by \drift (in cents)
    var breathLFO = SinOsc.kr(1/4, 0, drift.lag(2));
    var f = sa * (2 ** (breathLFO / 1200));  // cents → frequency ratio

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

    // Pa string — perfect fifth (3:2) + overtones, uses drifted freq
    pa = CombL.ar(excite_pa, 1/20.0, 1/(f*1.5), 8.0)
       + CombL.ar(excite_pa, 1/20.0, 1/(f*3.0), 5.6) * 0.3
       + CombL.ar(excite_pa, 1/20.0, 1/(f*4.5), 4.0) * 0.15;

    // Sa string 1 — fundamental + overtones
    sa1 = CombL.ar(excite_sa1, 1/20.0, 1/f, 10.0)
        + CombL.ar(excite_sa1, 1/20.0, 1/(f*2), 7.0) * 0.3
        + CombL.ar(excite_sa1, 1/20.0, 1/(f*3), 5.0) * 0.15;

    // Sa string 2 — slight detune (3.5 cents)
    sa2 = CombL.ar(excite_sa2, 1/20.0, 1/(f*1.002), 10.0)
        + CombL.ar(excite_sa2, 1/20.0, 1/(f*2.004), 7.0) * 0.3
        + CombL.ar(excite_sa2, 1/20.0, 1/(f*3.006), 5.0) * 0.15;

    // Sa low — octave below + overtones
    sa_low = CombL.ar(excite_salow, 1/20.0, 1/(f*0.5), 12.0)
           + CombL.ar(excite_salow, 1/20.0, 1/f, 8.4) * 0.3
           + CombL.ar(excite_salow, 1/20.0, 1/(f*1.5), 6.0) * 0.15;

    // ── Wave field partials: Ga (minor 3rd, 6:5) and Ma (4th, 4:3)
    // These are additive sinusoidal partials, not physical strings
    // .lag(2) gives 2-second crossfade when amplitudes change
    ga_str = SinOsc.ar(f * 1.2, 0, amp_ga.lag(2) * 0.15)
           + SinOsc.ar(f * 1.201, 0, amp_ga.lag(2) * 0.05);  // slight chorus
    ma_str = SinOsc.ar(f * 1.333, 0, amp_ma.lag(2) * 0.15)
           + SinOsc.ar(f * 1.335, 0, amp_ma.lag(2) * 0.05);

    // Jivari — gentle waveshaping for buzz
    pa     = pa     * 0.8;
    sa1    = sa1    * 0.8;
    sa2    = sa2    * 0.8;
    sa_low = sa_low * 0.8;

    // Mix: physical strings + wave field partials
    mix = (pa * amp_pa.lag(2)) + (sa1 * amp_sa1.lag(2))
        + (sa2 * amp_sa2.lag(2)) + (sa_low * amp_salow.lag(2))
        + ga_str + ma_str;

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
// SYNTHDEF 3 — MELODIC NOTE (single swara with gamak)
// Gamaks are not ornaments — they ARE the note (Pearson 2016)
// ======================================================

SynthDef(\raga_note, {
    |out=0, freq=261.63, amp=0.4,
     dur=1.0, gamaka=0, gamaka_rate=5,
     gamaka_depth=0.015, pan=0|

    var sig, env, freq_mod;

    // Gamaka types: 0=none 1=kampita 2=andolan 3=meend
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        freq * (1 + SinOsc.ar(gamaka_rate * 0.4, 0, gamaka_depth * 0.6)),
        freq * (1 + XLine.ar(0.05, 0.001, dur * 0.3)),
    ]);

    sig = Pluck.ar(WhiteNoise.ar(0.3), Impulse.ar(0),
        1/20.0, 1/freq_mod, dur * 2, 0.25);
    sig = sig + (SinOsc.ar(freq_mod, 0, 0.1) *
        EnvGen.ar(Env.perc(0.01, dur * 0.8)));
    env = EnvGen.ar(
        Env.new([0, 1, 0.7, 0], [0.005, dur * 0.7, dur * 0.25]),
        doneAction: 2);
    Out.ar(out, Pan2.ar(sig * amp * env, pan));
}).store;

// ======================================================
// SYNTHDEF 3b — CONTINUOUS RAGA PHRASE
// Pitch envelope across multiple swaras — gamaks AS notes
// Source: Pearson 2016 — gamakas are continuous pitch events
// ======================================================

SynthDef(\raga_phrase, {
    |out=0, freq1=240, freq2=270, freq3=320,
     dur1=0.5, dur2=0.5, dur3=1.0,
     gamak_rate=3, gamak_depth=30,
     gamak_note=1, amp=0.4, pan=0|

    var totalDur, pitchEnv, andolan, sig, env;

    totalDur = dur1 + dur2 + dur3;

    // Continuous pitch envelope — the phrase IS the pitch curve
    pitchEnv = EnvGen.kr(
        Env([freq1, freq2, freq3], [dur1, dur2], \exponential)
    );

    // Andolan on specified note position
    // Activates during the gamak_note segment only
    andolan = SinOsc.kr(gamak_rate) * gamak_depth *
        Select.kr(gamak_note, [
            EnvGen.kr(Env([1,1,0,0], [dur1, 0.01, dur2+dur3-0.01])),
            EnvGen.kr(Env([0,0,1,1,0], [dur1, 0.01, dur2-0.02, 0.01])),
            EnvGen.kr(Env([0,0,0,1], [dur1+dur2, 0.01, dur3-0.01])),
        ]);

    // Sarangi-like bowed timbre for phrase
    sig = Saw.ar(pitchEnv + andolan, 0.3) +
          SinOsc.ar(pitchEnv + andolan, 0, 0.5) +
          Saw.ar((pitchEnv + andolan) * 2.01, 0.08);
    sig = LPF.ar(sig, (pitchEnv + andolan) * 4);

    env = EnvGen.ar(
        Env.new([0, 1, 0.8, 0], [0.01, totalDur * 0.85, totalDur * 0.14]),
        doneAction: 2);

    Out.ar(out, Pan2.ar(sig * amp * env, pan));
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
// SYNTHDEF 6 — SARANGI NOTE
// Bowed gut string — the voice of the raga.
// Physical model: CombL delay-line strings with bow excitation.
// Odd harmonics dominate. Gut inharmonicity. Nasal body.
// Three main strings (Sa Pa Sa+) + sympathetic taraf ring.
// Modeled from sarangi_voice.py additive engine.
// ======================================================

SynthDef(\sarangi_note, {
    |out=0, freq=261.63, amp=0.45,
     dur=2.0, bow=0.55, gamaka=0,
     gamaka_rate=5.2, gamaka_depth=0.006, pan=0|

    var sig, bow_excite, string, taraf, body, env, freq_mod;
    var h2, h3, h5;

    // Gamaka
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        freq * (1 + SinOsc.ar(gamaka_rate * 0.4, 0, gamaka_depth * 1.5)),
        freq * (1 + XLine.ar(0.04, 0.001, dur * 0.3)),
    ]);

    // Bow excitation — continuous friction noise, not impulse
    bow_excite = LPF.ar(PinkNoise.ar(0.25 * bow), freq_mod * 3)
        + Dust.ar(freq_mod * 0.5, 0.08 * bow); // rosin grain

    // Physical string — CombL delay line at fundamental
    string = CombL.ar(bow_excite, 0.05, freq_mod.reciprocal, dur * 4);

    // Gut string odd-harmonic emphasis — bowed strings ring odd partials
    // Inharmonicity factor B=0.0006 (gut string stretching)
    h2 = CombL.ar(bow_excite * 0.20, 0.05, (freq_mod * 2 * (1 + 0.0024).sqrt).reciprocal, dur * 2.8);
    h3 = CombL.ar(bow_excite * 0.55, 0.05, (freq_mod * 3 * (1 + 0.0054).sqrt).reciprocal, dur * 2.0);
    h5 = CombL.ar(bow_excite * 0.30, 0.05, (freq_mod * 5 * (1 + 0.015).sqrt).reciprocal, dur * 1.2);

    sig = string + h2 + h3 + h5;

    // Sympathetic taraf — faint ringing at octave and fifth
    taraf = CombL.ar(sig * 0.04, 0.05, (freq_mod * 2).reciprocal, dur * 3)
          + CombL.ar(sig * 0.025, 0.05, (freq_mod * 1.5).reciprocal, dur * 3.5);

    sig = sig + taraf;

    // Nasal body resonance — skin membrane ~400Hz peak, ~800Hz notch
    body = BPF.ar(sig, 400, 0.35) * 2.0;
    sig = sig + body;
    sig = BRF.ar(sig, 800, 0.4);

    // Bow pressure vibrato — delayed onset, slow
    sig = sig * (1 + (
        SinOsc.kr(gamaka_rate * 0.9, 0, 0.03 * bow) *
        EnvGen.kr(Env([0, 0, 1], [dur * 0.2, dur * 0.3]))
    ));

    env = EnvGen.ar(
        Env.new([0, 1, 0.85, 0], [0.04, dur * 0.7, dur * 0.26]),
        doneAction: 2);

    sig = Limiter.ar(sig, 0.8);
    Out.ar(out, Pan2.ar(sig * amp * env, pan));
}).store;

// ======================================================
// SYNTHDEF 7 — MRIDANGAM BOL
// Carnatic barrel drum — both heads tuned to Sa.
// Near-perfect harmonic overtone series (unique among drums).
// Ramamatya's 16th-c. tuning: head modes at 1:1.56:2:2.61:3
// Right (valanthalai): tuned, ringing. Left (thoppi): bass drop.
// 0=Tha 1=Dhi 2=Thom 3=Nam 4=Dhin 5=Ki 6=Ta
// ======================================================

SynthDef(\mridangam_bol, {
    |out=0, bol=0, freq=130.81, amp=0.5|

    var right, left, strike, sig, env;
    var rAmp, lAmp, rFreq, lFreq, rDecay, lDecay;
    var rMembrane, rMode2, rMode3, rMode4, rMode5;

    rAmp   = Select.kr(bol, [0.6,  0.7,  0.0,  0.6,  0.7,  0.5,  0.6]);
    lAmp   = Select.kr(bol, [0.5,  0.3,  0.9,  0.0,  0.5,  0.0,  0.0]);
    rFreq  = Select.kr(bol, [1.0,  1.0,  1.0,  1.5,  1.0,  2.0,  1.5]) * freq;
    lFreq  = Select.kr(bol, [0.5,  0.5,  0.4,  0.5,  0.5,  0.5,  0.5]) * freq;
    rDecay = Select.kr(bol, [0.15, 0.30, 0.12, 0.08, 0.28, 0.05, 0.06]);
    lDecay = Select.kr(bol, [0.25, 0.20, 0.45, 0.25, 0.25, 0.25, 0.25]);

    // Right head — CombL delay-line membrane at harmonic modes
    // Mridangam modes: 1.0, 1.56, 2.0, 2.61, 3.0 (Ramamatya ratios)
    rMembrane = Pluck.ar(WhiteNoise.ar(0.5), Impulse.ar(0),
        0.05, rFreq.reciprocal, rDecay * 3, 0.3);
    rMode2 = Pluck.ar(WhiteNoise.ar(0.25), Impulse.ar(0),
        0.05, (rFreq * 1.56).reciprocal, rDecay * 2.5, 0.3) * 0.45;
    rMode3 = Pluck.ar(WhiteNoise.ar(0.15), Impulse.ar(0),
        0.05, (rFreq * 2.0).reciprocal, rDecay * 2, 0.3) * 0.3;
    rMode4 = Pluck.ar(WhiteNoise.ar(0.1), Impulse.ar(0),
        0.05, (rFreq * 2.61).reciprocal, rDecay * 1.5, 0.3) * 0.15;
    rMode5 = Pluck.ar(WhiteNoise.ar(0.08), Impulse.ar(0),
        0.05, (rFreq * 3.0).reciprocal, rDecay * 1.2, 0.3) * 0.1;
    right = rMembrane + rMode2 + rMode3 + rMode4 + rMode5;
    right = HPF.ar(right, 100);

    // Left head — bass membrane with pitch drop (clay-loaded)
    left = SinOsc.ar(
        XLine.ar(lFreq, lFreq * 0.55, lDecay * 0.5), 0, 0.7
    ) * EnvGen.ar(Env.perc(0.002, lDecay));
    left = left + Pluck.ar(
        WhiteNoise.ar(0.3), Impulse.ar(0),
        0.05, lFreq.reciprocal, lDecay * 2, 0.2) * 0.4;
    left = LPF.ar(left, 400);

    // Palm strike transient
    strike = BPF.ar(WhiteNoise.ar(0.4), 1200, 0.4) *
        EnvGen.ar(Env.perc(0.001, 0.02));

    sig = (right * rAmp) + (left * lAmp) + (strike * 0.3);

    // Barrel body resonance
    sig = sig + FreeVerb.ar(sig, 0.06, 0.12, 0.15) * 0.12;

    env = EnvGen.ar(Env.perc(0.001, 0.5), doneAction: 2);
    Out.ar(out, sig * amp * env ! 2);
}).store;

// ======================================================
// SYNTHDEF 8 — PAKHAWAJ BOL
// Dhrupad barrel drum — deeper, longer than mridangam.
// Larger barrel body. Thunderous bass. Lower tuning.
// Both heads struck with full palms — massive transient.
// 0=Ge 1=Dha 2=Din 3=Ta 4=Tete 5=Ka 6=Ghen
// ======================================================

SynthDef(\pakhawaj_bol, {
    |out=0, bol=0, freq=110, amp=0.5|

    var right, left, strike, sig, env;
    var rAmp, lAmp, rDecay, lDecay, lDrop;

    rAmp   = Select.kr(bol, [0.0,  0.6,  0.7,  0.6,  0.5,  0.0,  0.3]);
    lAmp   = Select.kr(bol, [0.9,  0.5,  0.0,  0.0,  0.0,  0.8,  0.8]);
    rDecay = Select.kr(bol, [0.20, 0.25, 0.30, 0.10, 0.08, 0.20, 0.22]);
    lDecay = Select.kr(bol, [0.55, 0.45, 0.35, 0.30, 0.30, 0.50, 0.50]);
    lDrop  = Select.kr(bol, [0.35, 0.45, 0.50, 0.50, 0.50, 0.30, 0.35]);

    // Right head — deep physical membrane, fewer modes than mridangam
    right = Pluck.ar(WhiteNoise.ar(0.5), Impulse.ar(0),
        0.05, freq.reciprocal, rDecay * 4, 0.25);
    right = right + Pluck.ar(WhiteNoise.ar(0.2), Impulse.ar(0),
        0.05, (freq * 2).reciprocal, rDecay * 3, 0.25) * 0.2;
    right = right + Pluck.ar(WhiteNoise.ar(0.1), Impulse.ar(0),
        0.05, (freq * 3).reciprocal, rDecay * 2, 0.25) * 0.08;

    // Left head — massive bass, slow pitch drop (thunderous)
    left = SinOsc.ar(
        XLine.ar(freq * 0.5, freq * lDrop, lDecay * 0.6), 0, 0.8
    ) * EnvGen.ar(Env.perc(0.003, lDecay));
    // Bass body resonance — the pakhawaj barrel rings
    left = left + CombL.ar(left * 0.3, 0.05, (freq * 0.5).reciprocal, lDecay * 1.5);
    left = LPF.ar(left, 280);

    // Heavy full-palm strike
    strike = LPF.ar(WhiteNoise.ar(0.5), 500) *
        EnvGen.ar(Env.perc(0.002, 0.05));

    sig = (right * rAmp) + (left * lAmp) + (strike * 0.25);

    // Large barrel body resonance — longer reverb than mridangam
    sig = sig + FreeVerb.ar(sig, 0.15, 0.3, 0.35) * 0.2;

    env = EnvGen.ar(Env.perc(0.001, 0.65), doneAction: 2);
    Out.ar(out, sig * amp * env ! 2);
}).store;

// ======================================================
// SYNTHDEF 9 — BANSURI NOTE
// Bamboo flute — Krishna's voice. Side-blown.
// Waveguide model: breath excites a tube (DelayL feedback loop).
// Overblowing at octave. Breathy air across embouchure.
// ======================================================

SynthDef(\bansuri_note, {
    |out=0, freq=261.63, amp=0.4,
     dur=1.5, breath=0.08, gamaka=0,
     gamaka_rate=4, gamaka_depth=0.008, pan=0|

    var sig, air, tube, excite, feedback, freq_mod, env;

    // Gamaka
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        freq * (1 + SinOsc.ar(gamaka_rate * 0.3, 0, gamaka_depth * 1.2)),
        freq * (1 + XLine.ar(0.03, 0.001, dur * 0.25)),
    ]);

    // Breath excitation — turbulent air across embouchure hole
    excite = BPF.ar(PinkNoise.ar(0.4), freq_mod * 2, 0.8) +
             LPF.ar(WhiteNoise.ar(0.15), freq_mod * 4);

    // Bamboo tube — delay-line waveguide
    tube = CombL.ar(excite, 0.05, freq_mod.reciprocal, dur * 3);
    // Octave partial — overblowing (weaker)
    tube = tube + CombL.ar(excite * 0.15, 0.05, (freq_mod * 2).reciprocal, dur * 2) * 0.25;
    // Faint third
    tube = tube + CombL.ar(excite * 0.05, 0.05, (freq_mod * 3).reciprocal, dur * 1.2) * 0.08;

    sig = tube;

    // Breath noise — side-blown character (air you hear across the hole)
    air = BPF.ar(PinkNoise.ar(breath), freq_mod * 1.5, 0.5);
    air = air + BPF.ar(PinkNoise.ar(breath * 0.4), freq_mod * 3, 0.4);
    sig = sig + air;

    // Bamboo body — warm LPF, no harsh highs
    sig = LPF.ar(sig, freq_mod * 5);

    // Breath vibrato — slower, delayed onset
    sig = sig * (1 + (
        SinOsc.kr(gamaka_rate * 0.8, 0, 0.025) *
        EnvGen.kr(Env([0, 0, 1], [dur * 0.25, dur * 0.2]))
    ));

    env = EnvGen.ar(
        Env.new([0, 0.7, 1, 0.8, 0], [0.06, 0.08, dur * 0.65, dur * 0.21]),
        doneAction: 2);

    Out.ar(out, Pan2.ar(sig * amp * env, pan));
}).store;

// ======================================================
// SYNTHDEF 10 — SITAR NOTE
// Steel string plucked with mizrab (wire plectrum).
// Jawari: flat curved bridge — string buzzes against it.
// 13 sympathetic taraf strings tuned to the raga.
// Physical model: Pluck + CombL taraf + jawari waveshaping.
// ======================================================

SynthDef(\sitar_note, {
    |out=0, freq=261.63, amp=0.4,
     dur=1.5, jawari=0.5, gamaka=0,
     gamaka_rate=5, gamaka_depth=0.012, pan=0|

    var main, main2, taraf, buzz, sig, env, freq_mod;

    // Gamaka
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        freq * (1 + SinOsc.ar(gamaka_rate * 0.4, 0, gamaka_depth * 0.8)),
        freq * (1 + XLine.ar(0.06, 0.001, dur * 0.35)),
    ]);

    // Main string — Karplus-Strong with steel brightness
    main = Pluck.ar(WhiteNoise.ar(0.5), Impulse.ar(0),
        0.05, freq_mod.reciprocal, dur * 4, 0.3);
    // Second course — slight detune for thickness
    main2 = Pluck.ar(WhiteNoise.ar(0.4), Impulse.ar(0),
        0.05, (freq_mod * 1.001).reciprocal, dur * 3.8, 0.3) * 0.3;
    main = main + main2;

    // Jawari buzz — flat bridge nonlinear waveshaping
    // The sitar's soul — string lifts off and slaps back against bridge
    buzz = (main * (1 + (jawari * 8))).tanh / (1 + (jawari * 8));
    main = (main * (1 - jawari)) + (buzz * jawari);

    // Sympathetic taraf strings — 13 strings ringing at raga intervals
    // Sa, Re, Ga, Ma, Pa, Dha, Ni + octaves — tuned to raga
    taraf = CombL.ar(main * 0.06, 0.05, (freq_mod * 2).reciprocal, dur * 3)     // Sa+
          + CombL.ar(main * 0.04, 0.05, (freq_mod * 1.5).reciprocal, dur * 3.5)  // Pa
          + CombL.ar(main * 0.035, 0.05, (freq_mod * 3).reciprocal, dur * 2)      // Sa++
          + CombL.ar(main * 0.03, 0.05, (freq_mod * 1.25).reciprocal, dur * 2.5)  // Ga (5/4)
          + CombL.ar(main * 0.025, 0.05, (freq_mod * 1.333).reciprocal, dur * 2.5) // Ma (4/3)
          + CombL.ar(main * 0.02, 0.05, (freq_mod * 1.667).reciprocal, dur * 2);   // Dha (5/3)

    // Mizrab strike transient — hard wire plectrum on steel
    sig = main + taraf;
    sig = sig + (HPF.ar(WhiteNoise.ar(0.1), 2500) *
        EnvGen.ar(Env.perc(0.0005, 0.012)));

    env = EnvGen.ar(
        Env.new([0, 1, 0.35, 0], [0.002, dur * 0.25, dur * 0.75]),
        doneAction: 2);

    sig = Limiter.ar(sig, 0.8);
    Out.ar(out, Pan2.ar(sig * amp * env, pan));
}).store;

// ======================================================
// SYNTHDEF 11 — SHEHNAI NOTE
// Double-reed conical bore — Indian oboe.
// Waveguide tube + reed nonlinearity + conical bore modes.
// Penetrating, festive. Bismillah Khan's voice.
// ======================================================

SynthDef(\shehnai_note, {
    |out=0, freq=261.63, amp=0.35,
     dur=2.0, reed=0.6, gamaka=0,
     gamaka_rate=5, gamaka_depth=0.01, pan=0|

    var excite, tube, bore, sig, env, freq_mod;

    // Gamaka
    freq_mod = Select.ar(gamaka, [
        DC.ar(freq),
        freq * (1 + SinOsc.ar(gamaka_rate, 0, gamaka_depth)),
        freq * (1 + SinOsc.ar(gamaka_rate * 0.35, 0, gamaka_depth * 1.3)),
        freq * (1 + XLine.ar(0.05, 0.001, dur * 0.3)),
    ]);

    // Reed excitation — double reed creates complex waveform
    // Nonlinear pressure-flow reed model
    excite = LPF.ar(WhiteNoise.ar(0.3), freq_mod * 6);
    excite = (excite * (1 + (reed * 5))).tanh / (1 + (reed * 5)); // reed nonlinearity
    excite = excite + (Pulse.ar(freq_mod, 0.48, 0.15 * reed)); // reed buzz component

    // Conical bore — CombL tube with multiple resonant modes
    // Conical bore supports both odd AND even harmonics (unlike clarinet)
    tube = CombL.ar(excite, 0.05, freq_mod.reciprocal, dur * 2);
    tube = tube + CombL.ar(excite * 0.5, 0.05, (freq_mod * 2).reciprocal, dur * 1.5) * 0.45;
    tube = tube + CombL.ar(excite * 0.3, 0.05, (freq_mod * 3).reciprocal, dur * 1.2) * 0.3;
    tube = tube + CombL.ar(excite * 0.15, 0.05, (freq_mod * 4).reciprocal, dur * 0.8) * 0.15;
    tube = tube + CombL.ar(excite * 0.08, 0.05, (freq_mod * 5).reciprocal, dur * 0.5) * 0.08;

    sig = tube;

    // Conical bore resonance — mid boost (penetrating quality)
    bore = BPF.ar(sig, 1200, 0.4) * 1.8;
    sig = sig + bore;

    // Bell radiation — slight high boost at flare
    sig = sig + HPF.ar(sig, 2000) * 0.15;

    // Breath pressure variation — circular breathing wobble
    sig = sig * (1 + SinOsc.kr(3.2 + LFNoise1.kr(0.4, 0.8), 0, 0.04));

    sig = LPF.ar(sig, freq_mod * 10);

    env = EnvGen.ar(
        Env.new([0, 0.85, 1, 0.8, 0], [0.015, 0.03, dur * 0.75, dur * 0.2]),
        doneAction: 2);

    sig = Limiter.ar(sig, 0.8);
    Out.ar(out, Pan2.ar(sig * amp * env, pan));
}).store;

// ======================================================
// SYNTHDEF 12 — BIJA DRONE
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
// WAVE FIELD RHYTHM — soft percussive pulse
// ======================================================

SynthDef(\bol, {
    |out=0, freq=400, amp=0.1, pan=0, decay=0.06|
    var env = EnvGen.kr(Env.perc(0.001, decay), doneAction: 2);
    var body = SinOsc.ar(freq, 0, 0.7) * env;
    var click = WhiteNoise.ar(0.3) * EnvGen.kr(Env.perc(0.001, 0.015));
    var sig = (body + click) * amp;
    sig = HPF.ar(sig, 80);  // remove sub-bass rumble
    Out.ar(out, Pan2.ar(sig, pan));
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

// ── Raga phrase OSC — continuous pitch envelope ──
// /atlas/phrase [freq1 freq2 freq3 dur1 dur2 dur3 gamak_rate gamak_depth gamak_note amp pan]
OSCFunc({ |msg|
    Synth(\raga_phrase, [
        \out, 0,
        \freq1,       msg[1] ? 240,
        \freq2,       msg[2] ? 270,
        \freq3,       msg[3] ? 320,
        \dur1,        msg[4] ? 0.5,
        \dur2,        msg[5] ? 0.5,
        \dur3,        msg[6] ? 1.0,
        \gamak_rate,  msg[7] ? 3,
        \gamak_depth, msg[8] ? 30,
        \gamak_note,  msg[9] ? 1,
        \amp,         msg[10] ? 0.35,
        \pan,         msg[11] ? 0,
    ]);
}, '/atlas/phrase');

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

// ── Sarangi OSC ──
// /atlas/sarangi/note [freq amp dur bow gamaka gamaka_rate gamaka_depth pan]
OSCFunc({ |msg|
    Synth(\sarangi_note, [
        \out,           0,
        \freq,          msg[1] ? 261.63,
        \amp,           msg[2] ? 0.45,
        \dur,           msg[3] ? 2.0,
        \bow,           msg[4] ? 0.55,
        \gamaka,        msg[5] ? 0,
        \gamaka_rate,   msg[6] ? 5.2,
        \gamaka_depth,  msg[7] ? 0.006,
        \pan,           msg[8] ? 0,
    ]);
}, '/atlas/sarangi/note');

// ── Mridangam OSC ──
// /atlas/mridangam [bol_idx amp freq]
OSCFunc({ |msg|
    Synth(\mridangam_bol, [
        \out,  0,
        \bol,  msg[1] ? 0,
        \amp,  msg[2] ? 0.5,
        \freq, msg[3] ? 130.81,
    ]);
}, '/atlas/mridangam');

// ── Pakhawaj OSC ──
// /atlas/pakhawaj [bol_idx amp freq]
OSCFunc({ |msg|
    Synth(\pakhawaj_bol, [
        \out,  0,
        \bol,  msg[1] ? 0,
        \amp,  msg[2] ? 0.5,
        \freq, msg[3] ? 110,
    ]);
}, '/atlas/pakhawaj');

// ── Bansuri OSC ──
// /atlas/bansuri/note [freq amp dur breath gamaka gamaka_rate gamaka_depth pan]
OSCFunc({ |msg|
    Synth(\bansuri_note, [
        \out,           0,
        \freq,          msg[1] ? 261.63,
        \amp,           msg[2] ? 0.4,
        \dur,           msg[3] ? 1.5,
        \breath,        msg[4] ? 0.08,
        \gamaka,        msg[5] ? 0,
        \gamaka_rate,   msg[6] ? 4,
        \gamaka_depth,  msg[7] ? 0.008,
        \pan,           msg[8] ? 0,
    ]);
}, '/atlas/bansuri/note');

// ── Sitar OSC ──
// /atlas/sitar/note [freq amp dur jawari gamaka gamaka_rate gamaka_depth pan]
OSCFunc({ |msg|
    Synth(\sitar_note, [
        \out,           0,
        \freq,          msg[1] ? 261.63,
        \amp,           msg[2] ? 0.4,
        \dur,           msg[3] ? 1.5,
        \jawari,        msg[4] ? 0.5,
        \gamaka,        msg[5] ? 0,
        \gamaka_rate,   msg[6] ? 5,
        \gamaka_depth,  msg[7] ? 0.012,
        \pan,           msg[8] ? 0,
    ]);
}, '/atlas/sitar/note');

// ── Shehnai OSC ──
// /atlas/shehnai/note [freq amp dur reed gamaka gamaka_rate gamaka_depth pan]
OSCFunc({ |msg|
    Synth(\shehnai_note, [
        \out,           0,
        \freq,          msg[1] ? 261.63,
        \amp,           msg[2] ? 0.35,
        \dur,           msg[3] ? 2.0,
        \reed,          msg[4] ? 0.6,
        \gamaka,        msg[5] ? 0,
        \gamaka_rate,   msg[6] ? 5,
        \gamaka_depth,  msg[7] ? 0.01,
        \pan,           msg[8] ? 0,
    ]);
}, '/atlas/shehnai/note');

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
"  /atlas/phrase         continuous raga phrase".postln;
"  /atlas/tabla          play single bol (0-6)".postln;
"  /atlas/tabla/start    start theka".postln;
"  /atlas/tabla/stop     stop theka".postln;
"  /atlas/santoor/note   hammered dulcimer".postln;
"  /atlas/sarangi/note   bowed gut string".postln;
"  /atlas/mridangam      carnatic barrel drum".postln;
"  /atlas/pakhawaj       dhrupad barrel drum".postln;
"  /atlas/bansuri/note   bamboo flute".postln;
"  /atlas/sitar/note     plucked + jawari + taraf".postln;
"  /atlas/shehnai/note   double reed".postln;
"  /atlas/bija           update bija drone".postln;
"  /atlas/master         global mix".postln;
"  /atlas/field          full field update".postln;
"".postln;

// ── Wave field modulation (from jyotisha engine) ──────────
// These handlers APPLY changes to sound, not just log them.

~gamakDepth = 0.3;
~waveBpm = 84;
~breathGamakProb = 0.5;
~breathDriftCents = 3.0;
~breathEnergy = 0.5;
~rhythmPrime = 7;
~rhythmSecondary = 3;
~rhythmBlend = 0.8;
~rhythmRunning = false;

// /atlas/wave/gamak — modulates gamak depth on melody
OSCFunc({ |msg|
    ~gamakDepth = msg[1].linlin(0, 1, 0.1, 0.8);
}, '/atlas/wave/gamak');

// /atlas/wave/bpm — sets wave tempo
OSCFunc({ |msg|
    ~waveBpm = msg[1];
}, '/atlas/wave/bpm');

// /atlas/wave/partial — logs dominant partial name
OSCFunc({ |msg|
    ("  \u2669 partial: " ++ msg[1].asString).postln;
}, '/atlas/wave/partial');

// /atlas/wave/k — logs dominant harmonic
OSCFunc({ |msg| }, '/atlas/wave/k');

// /atlas/wave/partials — SET tanpura partial amplitudes in real time
OSCFunc({ |msg|
    var pairs = msg[1..].clump(2);
    pairs.do({ |pair|
        var ratio = pair[0], ampVal = pair[1];
        if(~tanpura.notNil, {
            case
                { (ratio - 1.0).abs < 0.05 }  { ~tanpura.set(\amp_sa1, ampVal * 0.35) }
                { (ratio - 1.2).abs < 0.05 }  { ~tanpura.set(\amp_ga, ampVal * 0.20) }
                { (ratio - 1.333).abs < 0.1 } { ~tanpura.set(\amp_ma, ampVal * 0.20) }
                { (ratio - 1.5).abs < 0.05 }  { ~tanpura.set(\amp_pa, ampVal * 0.25) };
        });
    });
    ("  \u2669 partials: " ++ pairs.collect({ |p| p[0].round(0.01) ++ "=" ++ p[1].round(0.01) }).join(" ")).postln;
}, '/atlas/wave/partials');

// /atlas/wave/rhythm_mode — set phrase grouping
OSCFunc({ |msg|
    ~rhythmPrime = msg[1].asInteger;
    ~rhythmSecondary = msg[2].asInteger;
    ~rhythmBlend = msg[3];
    ("  \u2669 rhythm: " ++ ~rhythmPrime ++ "/" ++ ~rhythmSecondary ++ " blend=" ++ ~rhythmBlend.round(0.01)).postln;
}, '/atlas/wave/rhythm_mode');

// /atlas/wave/breath — SET tanpura drift + store breath params
OSCFunc({ |msg|
    ~breathGamakProb = msg[1];
    ~breathDriftCents = msg[2];
    ~breathEnergy = msg[3];
    // Apply drift to tanpura — the SynthDef's internal LFO uses this
    if(~tanpura.notNil, {
        ~tanpura.set(\drift, ~breathDriftCents);
    });
}, '/atlas/wave/breath');

// /atlas/wave/hora — log only (slow timescale, future use)
OSCFunc({ |msg|
    ("  \u2669 hora: " ++ msg[1].asString ++ " w=" ++ msg[2].round(0.01)).postln;
}, '/atlas/wave/hora');

// /atlas/natal/raga — log natal home raga
OSCFunc({ |msg|
    ("  \u2669 natal raga: " ++ msg[1].asString).postln;
}, '/atlas/natal/raga');

// /atlas/natal/partial_emphasis — log natal partial
OSCFunc({ |msg|
    ("  \u2669 natal partial: " ++ msg[1].round(0.01) ++ " w=" ++ msg[2].round(0.01)).postln;
}, '/atlas/natal/partial_emphasis');

// ── Rhythm Task — soft percussive pulse in prime groupings ──
~rhythmTask = Task({
    ("  \u2669 rhythm task started").postln;
    loop {
        var prime, secondary, blend, dur;
        prime = ~rhythmPrime ? 7;
        secondary = ~rhythmSecondary ? 3;
        blend = ~rhythmBlend ? 0.8;
        dur = 60 / (~waveBpm ? 90) / 2;  // eighth note

        // Decide: dominant or secondary grouping (coin flip weighted by blend)
        if(blend.coin, {
            // Dominant prime grouping
            prime.do({ |i|
                var accent = if(i == 0, 1.0, 0.4);
                var freq = if(i == 0, 280, 420);
                Synth(\bol, [
                    \freq, freq,
                    \amp, 0.06 * accent * (~breathEnergy ? 0.5),
                    \decay, 0.05,
                    \pan, 0.2.rand2,
                ]);
                dur.wait;
            });
        }, {
            // Secondary prime grouping
            secondary.do({ |i|
                var accent = if(i == 0, 1.0, 0.35);
                var freq = if(i == 0, 240, 380);
                Synth(\bol, [
                    \freq, freq,
                    \amp, 0.04 * accent * (~breathEnergy ? 0.5),
                    \decay, 0.04,
                    \pan, 0.3.rand2,
                ]);
                dur.wait;
            });
        });
        // One eighth rest between groups
        dur.wait;
    }
});

// Start rhythm after a short delay
SystemClock.sched(2.0, {
    ~rhythmTask.play;
    ~rhythmRunning = true;
    nil;
});

"  wave handlers active:".postln;
"    /atlas/wave/gamak bpm partial k partials rhythm_mode breath hora".postln;
"    /atlas/natal/raga partial_emphasis".postln;
"    rhythm task: prime grouping pulse".postln;
"    tanpura drift: 4s prana breath cycle".postln;
"".postln;

}; // end fork

// Keep sclang alive
Routine({ loop { 1.0.wait } }).play(AppClock);
