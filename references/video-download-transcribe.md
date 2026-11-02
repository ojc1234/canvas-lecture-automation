# Download + transcribe a Canvas lecture video

1. bsk navigate to `/courses/<c>/modules/items/<id>`, then read the nested iframe src inside `iframe[title="도구 내용"]`: `https://common.jejunu.ac.kr/em/<content_id>?...`.
2. Navigate to `https://common.jejunu.ac.kr/em/<content_id>` and sync-XHR `/viewer/ssplayer/uniplayer_support/content.php?content_id=<id>` → `<media_uri>` = `https://jeju-cms-object.cdn.gov-ntruss.com/contents4/jjuuni1001/<id>/contents/media_files/mobile/ssmovie.mp4`.
3. Plain `curl -H 'Referer: https://common.jejunu.ac.kr/'` downloads it (no cookies needed). Save on E: (C: is low).
4. No captions exist (`media_script_list.xml` 404) → faster-whisper in the Hermes venv (`.../hermes-agent/venv/Scripts/python.exe`). GPU (GTX 1650) needs cuBLAS/cuDNN: installed at `E:\pylibs\cuda12` (`pip install --target E:/pylibs/cuda12 --no-deps nvidia-cublas-cu12 nvidia-cudnn-cu12==9.*`); call `os.add_dll_directory` on `nvidia\cublas\bin` and `nvidia\cudnn\bin` + prepend PATH. medium int8_float16 ≈ 6x realtime on GPU; CPU ≈ 1x and pegs the CPU (user objected) — use GPU.
5. Script template: `E:\lectures\43302\transcribe.py`. Run it as a background process with notify; stdout via `-u`.
6. Fix STT legal-term errors when summarising (담압→담합, 성관주의→선관주의, 형행화→형해화, 팔레→판례, 배우자→배후자).
