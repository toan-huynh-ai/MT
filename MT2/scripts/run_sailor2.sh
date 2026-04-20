#!/bin/bash
#SBATCH --job-name=sailor2_all
#SBATCH --output=/datastore/npl/luannt/IHSD/logs/sailor2_all.out
#SBATCH --error=/datastore/npl/luannt/IHSD/logs/sailor2_all.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=mps:a100:1
#SBATCH --mem=24G
#SBATCH --time=72:00:00

# =========================================================
# VRAM CONFIGURATION
# =========================================================
REQUIRED_VRAM=25000

# =========================================================
# CHUẨN BỊ MÔI TRƯỜNG
# =========================================================
module clear -f

module load shared python312
source /datastore/npl/luannt/IHSD/.cache/venv/bin/activate
export PATH="/datastore/npl/luannt/IHSD/.cache/venv/bin:$PATH"
export PYTHONPATH="/datastore/npl/luannt/IHSD/.cache/venv/lib/python3.12/site-packages:$PYTHONPATH"
cd /datastore/npl/luannt/IHSD/MT/MT

unset CUDA_VISIBLE_DEVICES
CHECK_OUT=$(/usr/local/bin/gpu_check.sh $REQUIRED_VRAM $SLURM_JOB_ID)
EXIT_CODE=$?
if [ $EXIT_CODE -eq 10 ]; then
    echo "$CHECK_OUT"
    exit 0
elif [ $EXIT_CODE -eq 11 ]; then
    echo "$CHECK_OUT"
    exit 1
fi
BEST_GPU=$CHECK_OUT
echo "✅ Job $SLURM_JOB_ID bắt đầu trên GPU: $BEST_GPU"

# =========================================================
# KHỞI TẠO PRIVATE MPS SERVER
# =========================================================
export CUDA_MPS_PIPE_DIRECTORY=/tmp/nvidia-mps-job$SLURM_JOB_ID
export CUDA_MPS_LOG_DIRECTORY=/tmp/nvidia-mps-log-job$SLURM_JOB_ID

rm -rf $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY
mkdir -p $CUDA_MPS_PIPE_DIRECTORY $CUDA_MPS_LOG_DIRECTORY

export CUDA_VISIBLE_DEVICES=$BEST_GPU
export PYTORCH_ALLOC_CONF=expandable_segments:True

# =========================================================
# CHẠY SAILOR2 TRANSLATION
# =========================================================
python /datastore/npl/luannt/IHSD/MT/MT/run_sailor2_8b.py --all