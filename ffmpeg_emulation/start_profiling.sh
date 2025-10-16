#!/bin/bash

for i in 36 37 38 40 41 42 43 44 45
do
    for j in $(seq 1 3)
    do
        echo "🚀 Running with $i FFmpeg task(s)..."
        sudo python3 multi_ffmpeg_profile.py --resolution 480p --num_tasks $i --execution_time 120
        echo "⏸️  Sleeping for 20 seconds..."
        sleep 20
    done
done

for i in 28 29 30 31 32 33 34 35
# for i in 14 16 18 20 22 24 25 26 27
do
    for j in $(seq 1 3)
    do
        echo "🚀 Running with $i FFmpeg task(s)..."
        sudo python3 multi_ffmpeg_profile.py --resolution 720p --num_tasks $i --execution_time 120
        echo "⏸️  Sleeping for 20 seconds..."
        sleep 20
    done
done

for i in 18 19 20 21 22 23 24 25 26
do
    for j in $(seq 1 3)
    do
        echo "🚀 Running with $i FFmpeg task(s)..."
        sudo python3 multi_ffmpeg_profile.py --resolution 1080p --num_tasks $i --execution_time 120
        echo "⏸️  Sleeping for 20 seconds..."
        sleep 20
    done
done


echo "✅ All benchmarks complete."


# ==== CPU = 15 ==== #
# Memory 16984
# 40 41 42 || 43 44 45 46 47 48
# 24 26 || 28 29 30 31 32 33 34 
# 18 19 20 21 22 23 24
# Memory 12844

# ==== CPU = 10 ==== #
# Memory 12844
# 36 37 38 40 41 42 43 44
# 14 16 18 20 22 24 25 26 27
# 16 17 18 19 20 21 22 23 24
# Memory 8192
# 32 34 36 37 38 40 42 
# 12 16 18 20 22 24 25 
# 12 14 15 16 17 18 19 20 21 

# ==== CPU = 5 ==== #
# Memory 8192
# 18 19 20 21 22
# 6 8 10 12 13 14 15 16 18 19 20
# 4 6 7 8 9 10 11 12 13 14 15
# Memory 4096
# 16 18 20 22 
# 12 14 16 18 19
# 6 8 10 12