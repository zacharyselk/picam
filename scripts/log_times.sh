# Writes the timestamps from a video to a .time.log file (not reliable)
ffprobe -show_frames $1 | grep best_effort_timestamp_time | grep -o '[0-9.]\+' > $1.time.log
