# Dapps-Analyzer

Levi

## Intro

To compare **similarity** and identify **external function call** within several minutes.

**The whole process is**:

1. Get the links of all dapps with specific category (eg. auction, trading, ...) using reptile
2. Download all dapps from the links
3. Find all `.sol` files from these dapps and generate a file list
4. Analyze these `.sol` files, compare the similarity, and find all external function call

### What is new!

(update 22.0330.01)

- Added more filter options (see **Instruction**).
- Now external call analysis support inheritance detection, all functions defined in the parent class will not be detected as external call.
- Instance detection (WIP): detect all instances declared in the contract and ignore their function call.
- Filtered more Solidity key words.

### Features

- The Analyzer can identify the duplicated code between two dapps.
- The Analyzer can identify the external function call in each dapp, it depends on my understanding of external function call, so it may not be abstractly correct.
- The Analyzer cannot identify the essential logic in each dapp, because the essential logic will vary according to the category of dapps.

### Dependency

Additional library `requests` and `bs4` are required by the reptile

```shell
pip install requests
pip install bs4
```

## Usage

### Command Line

```shell
python main.py [-c <category>] [-a <amount>] [<features>] [<options>]
```

Example:

Analyze 100 trading dapps (compare contracts only, ignore default files and contracts):

```shell
python3 ./main.py -c trading -A --mode contract --igfile --igcon
```

### Instruction

- `-c` is used to specify your category (such as auction, trading, ...), no quotation marks are required

- `-a` is used to specify the amount of dapps you want to download and analyze, default value is 100.

  Note that you **MUST** make sure that the amount is **no more than** the total amount of dapps that can be found on GitHub, otherwise the reptile will be stuck in an infinite loop.

- features:

  - `-C` is used to clear all generated files
  - `-A` is used to run the whole process automatically, which contains the following process:
    - `-r` is used to run the reptile separately
    - `-d` is used to download dapps separately
    - `-s` is used find all `.sol` files separately
    - `-m` is used to run the similarity comparison separately
    - `-e` is used to run the external detection separately

- [!New] options:

  - `--mode` is uesd to specify a compare mode from `program, contract, function`

    If you select `program`, it will compare programs and will not compare contracts; if you select `contract`, it will compare programs and contracts and will not compare functions.

    The default mode is `function`, to show all details.

  - `--igfile` is uesd to specify the file or diretory names you want to ignore

    All the files whose path include the specified names will be ignore.

    The default value is `Migrations.sol,node_modules`

  - `--igcon` is uesd to specify the contract names you want to ignore

    The default value is `Migrations`

### Hints

- If you run the above steps separately, make sure that the previous steps have been completed.
- The reptile uses a delay mechanism, that is, to request a web page every **10 seconds**, in order to avoid the robot detection of the website. If a download is incomplete, the delay will increase and try again, so please make sure that the dapp list contains all the dapps you need.

## Results

### Files

- The dapps will be downloaded in directory `./contracts`
- The names and links of dapps will be stored in `dapp_link.csv`
- All the path of `.sol` file will be recorded in `sol.log`
- The comparison results will be stored in `similarity.log`
- The external detection results will be stored in `external.log`

### Representation

#### Similarity Log

Example of `Similarity.log`:

```
------------------------------001 : dapp------------------------------
>> 022 : vixx:
{
	'001/dapp/Gaurd.sol::022/vixx/token.sol': completely same
}
>> 071 : Acropolis:
{
	'001/dapp/owned.sol::071/Acropolis/CryptoArt.sol':
	{
		'contract owned::contract owned':
		{
			'function owned ( )::function owned ( )': completely same
		}
	}
}
```

- The horizontal dash line divides each dapp, the example shown above is the comparison result of the dapp named "dapp", and the index is "001".

- Each symbol `>>` indicates the comparison with an other dapp, for example `>> 022 : vixx: ` means the results of compare dapp "001" with "022".

- Symbol `::` indicates the comparison between two `.sol` files or contracts or functions.

- The comparison results between two dapps are shown in a dictionary. One `Dapp` contains several `.sol` files; each file is a `Program`, containing several `Contract`; each contract contains several `Function`.

  In the dictionary, each key is the comparison object pair, the value is the comparison result.

  If `A.sol` is complete the same with `B.sol`, the result will be `'A.sol::B.sol': completely same`; if not completely the same, my program will check whether there are some contract are same in `A.sol` and `B.sol`; if the contracts are not completely the same, my program will check each function. If all functions are not similar, there will be no result.

- For each `.sol` file or contract, the comparison result will be either "completely the same" or showing details.

- For each function, the comparison result will be either "completely the same" or "same signature", which means that the function signatures are the same, while the implementations are different.

#### External Log

Example of `external.log`:

```
--------------------------------008 : Lokian.eth--------------------------------
{
	'008/Lokian.eth/src/project.eth.sol':
	{
		'contract Cryptomons is ERC1155Holder':
		{
			'function deposit ( uint256 amount ) public onlyManager': ['_token.allowance', '_token.transferFrom'],
			'function withdraw ( uint256 amount ) public onlyManager': ['_token.balanceOf', '_token.transfer'],
			'function burn ( uint256 amount ) public': ['_token.allowance', '_token.balanceOf', '_token.burnFrom'],
		}
	}
}
```

- The dictionary structure is almost the same as `similarity.log`.
- For each function, the key is the signature of this function, the value is a list containing the names of all external call.

## Other

- Some features are still improving.
- Please feel free to let me know if there are any problems or bugs.
- Enjoy!
