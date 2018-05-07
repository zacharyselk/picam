#ffmpeg -i $1 -map 0:v:0 -c copy -f null - 2>&1 | awk '/frame=/ {print $2}'
#ffmpeg -i $1 2>&1 | sed -n "s/.*, \(.*\) fps.*/\1/p"
ffprobe -show_streams -count_frames -pretty $1 | grep nb_read_frames
