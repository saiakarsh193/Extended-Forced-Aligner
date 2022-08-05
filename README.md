# Extended Forced Aligner  

Extended Forced Aligner using [Aeneas](https://www.readbeyond.it/aeneas/docs/index.html#) package in Python.  
It alignes with default align window size of 5 min.  
Currently supports English and Hindi (and other languages supported by [Aeneas](https://www.readbeyond.it/aeneas/docs/language.html)).  

## Running the aligner  

Install Aeneas dependencies (you will need `gcc` if you dont already have it)  

```bash
sudo apt install ffmpeg espeak libespeak-dev
```

Create a new python virtual environment and activate it.  

```bash
python -m venv env_align
source env_align/bin/activate
```

Install `numpy` first,  

```bash
pip install numpy
```

and then install the other packages.  

```bash
pip install -r requirements.txt 
```

The `extend_aligner.py` has argparse in it. So you can call with `--help` flag for details.  

```bash
python extend_aligner.py --help
```

and add parameters to the above command appropriately for running the code.  

