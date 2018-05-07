ffprobe -show_frames $1 | grep best_effort_timestamp= | grep -o '[0-9]\+' > $1.log 
