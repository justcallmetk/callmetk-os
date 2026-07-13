import csv
import math
import struct
import wave
from pathlib import Path

from ctk.cli import main
from ctk.music.analyzer import analyze_audio_file, analyze_folder
from ctk.music.cluster import cluster_tracks
from ctk.music.dna import build_creative_dna
from ctk.music.ep_builder import build_ep_recommendation


def make_wav(path: Path, frequency: float, amplitude: float = 0.4, seconds: float = 0.15, sample_rate: int = 8000) -> None:
    frames = []
    for index in range(int(sample_rate * seconds)):
        value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * index / sample_rate))
        frames.append(struct.pack('<h', value))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b''.join(frames))


def test_analyze_wav_extracts_local_features(tmp_path: Path):
    song = tmp_path / 'song.wav'
    make_wav(song, 220)
    result = analyze_audio_file(song)
    assert result.analysis_status == 'complete'
    assert result.duration_seconds > 0
    assert result.sample_rate == 8000
    assert result.channels == 1
    assert result.rms > 0
    assert result.energy > 0


def test_unsupported_audio_is_honest(tmp_path: Path):
    song = tmp_path / 'song.mp3'
    song.write_bytes(b'not a real mp3')
    result = analyze_audio_file(song)
    assert result.analysis_status == 'unsupported'
    assert result.tempo_bpm is None


def test_folder_analysis_writes_csv(tmp_path: Path):
    folder = tmp_path / 'audio'
    make_wav(folder / 'one.wav', 220)
    make_wav(folder / 'two.wav', 440)
    output = tmp_path / 'analysis.csv'
    results = analyze_folder(folder, output)
    assert len(results) == 2
    with output.open(newline='', encoding='utf-8') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 2
    assert rows[0]['track_id'].startswith('CTK-TRK-')


def test_clustering_and_ep_recommendation(tmp_path: Path):
    input_csv = tmp_path / 'analysis.csv'
    fields = ['track_id','title','path','format','duration_seconds','sample_rate','channels','sample_width_bits','peak','rms','energy','brightness','tempo_bpm','musical_key','analysis_status','analysis_notes']
    rows = []
    for index in range(6):
        rows.append({
            'track_id': f'T{index}', 'title': f'Track {index}', 'path': f'{index}.wav', 'format': 'wav',
            'duration_seconds': 180 + index, 'sample_rate': 44100, 'channels': 2, 'sample_width_bits': 16,
            'peak': 0.8, 'rms': 0.2, 'energy': 0.2 if index < 3 else 0.85,
            'brightness': 0.25 if index < 3 else 0.8, 'tempo_bpm': 80 + index if index < 3 else 120 + index,
            'musical_key': 'Em', 'analysis_status': 'complete', 'analysis_notes': '',
        })
    with input_csv.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    cluster_csv = tmp_path / 'clusters.csv'
    clustered = cluster_tracks(input_csv, cluster_csv, clusters=2)
    assert clustered.clusters == 2
    assert len(clustered.assignments) == 6
    decision = build_ep_recommendation(cluster_csv, tracks=3)
    assert decision.validate() == []
    assert decision.requires_approval is True
    assert decision.estimated_cost_usd == 0
    assert decision.evidence


def test_creative_dna(tmp_path: Path):
    path = tmp_path / 'analysis.csv'
    fields = ['duration_seconds','tempo_bpm','energy','brightness','musical_key','analysis_status']
    with path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows([
            {'duration_seconds':'180','tempo_bpm':'90','energy':'0.4','brightness':'0.3','musical_key':'Em','analysis_status':'complete'},
            {'duration_seconds':'240','tempo_bpm':'100','energy':'0.6','brightness':'0.5','musical_key':'Em','analysis_status':'complete'},
        ])
    dna = build_creative_dna(path)
    assert dna['tracks'] == 2
    assert dna['average_tempo_bpm'] == 95.0
    assert dna['most_common_keys'] == ['Em']


def test_music_cli_pipeline(tmp_path: Path, capsys):
    folder = tmp_path / 'audio'
    for index, frequency in enumerate((180, 220, 440, 520)):
        make_wav(folder / f'track-{index}.wav', frequency, amplitude=0.2 + index * 0.15)
    analysis = tmp_path / 'analysis.csv'
    clusters = tmp_path / 'clusters.csv'
    assert main(['music','analyze',str(folder),str(analysis)]) == 0
    assert main(['music','cluster',str(analysis),str(clusters),'--clusters','2']) == 0
    assert main(['music','ep-build',str(clusters),'--tracks','2']) == 0
    assert main(['music','dna',str(analysis)]) == 0
    output = capsys.readouterr().out
    assert 'Analyzed 4 audio file(s)' in output
    assert 'Clustered 4 track(s)' in output
    assert 'requires_approval' in output
    assert 'average_energy' in output
