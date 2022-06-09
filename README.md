# Extended-Forced-Aligner  

Extended Forced Aligner using [Aeneas](https://www.readbeyond.it/aeneas/docs/index.html#) package in Python.  
It alignes with default align window size of 5 min.  
Currently supports English and Hindi (and other languages supported by [Aeneas](https://www.readbeyond.it/aeneas/docs/language.html)).  

# Run the aligner  

Create a new python virtual environment and activate it.  

```bash
python -m venv env_align
source env_align/bin/activate
```

**Note: First install numpy seperately because Aeneas cannot be installed without proper numpy installation.**  

Install the required version of numpy using,  

```bash
python -m pip install numpy===1.22.3
```

and you can install the rest of the packages from `requirements.txt` using,  

```bash
python -m pip install -r requirements.txt
```


The `extend_aligner.py` has argparse in it. So you can call with `--help` flag for details.  

```bash
python extend_aligner.py --help
```

and add parameters to the above command appropriately for running the code.  

