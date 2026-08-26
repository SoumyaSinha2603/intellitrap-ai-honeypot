# IntelliTrap — adaptive AI honeypot

A honeypot backend that scores an attacker session by combining three independent signals rather
than trusting any one of them: a supervised classifier over request-log features, an unsupervised
anomaly score, and a sequence model over the attacker's request path.

> **Status — early prototype.** Docker-stable at v1.0 and not developed since March 2026. The
> blend weights below are hand-set, not fitted, and there is **no held-out evaluation of the
> threat score**. Read this as an architecture sketch, not a result. The evaluated, six-person
> continuation of this line of work is
> [adaptive-honeypot-security-system](https://github.com/SoumyaSinha2603/adaptive-honeypot-security-system).

## The threat score

Three signals blended into a 0–100 score (`ml/threat_scoring.py`):

| Weight | Signal | Model |
| --- | --- | --- |
| 0.5 | Probability the session's request log is malicious | Supervised classifier — `log_classifier.pkl` |
| 0.3 | How far the session sits from normal traffic | Isolation Forest — `anomaly_detector.pkl` |
| 0.2 | Session length relative to the longest observed | Heuristic on `request_count` |

Separately, an LSTM (`ml/lstm_attack_path_model.h5`) is trained over request sequences to predict
the attacker's **next step**. That is the piece intended to make the honeypot adaptive rather
than a static classifier — it lets the environment be shaped ahead of where the attacker is going.

## Features

Five per-session features, in `ml/attacker_dataset.csv`:

`request_count` · `unique_endpoints` · `avg_time_gap` · `avg_payload_entropy` · `sql_keyword_count`

## Layout

```
backend/app/
  routes/        api, auth, admin, files, threat
  core/          threat_state, threat_updater, logger
  models/        event
ml/
  feature_engineering.py   sequence_builder.py
  train_classifier.py      train_anomaly_detector.py
  lstm_train.py            predict_next_step.py
  threat_scoring.py        blends the three signals
data/logs/
```

FastAPI backend, `docker-compose up` to run.

## Honest limitations

- **The dataset is small and imbalanced** — 291 sessions, 36 of them labelled malicious. That is
  too little to support a claimed detection rate, which is why none is claimed here.
- **The blend weights (0.5 / 0.3 / 0.2) were chosen by hand.** They are a starting point, not a
  tuned result.
- **No held-out evaluation.** Nothing here reports precision, recall, or AUROC, because nothing
  here was measured on data the models had not seen.
- **`/api/threat/status` reads the most recent CSV row** rather than scoring live traffic — the
  serving path is a stub.
- The LSTM's next-step predictions are not wired into the honeypot's response behaviour yet.
