import os
import json
from os import environ
from datetime import datetime
from utils.config import validatorToolbox

def runStats() -> str:
    timeNow = datetime.now()
    ourShard = environ.get("SHARD")
    ourNetwork = environ.get("NETWORK_SWITCH")
    remote_shard_0 = [f'{validatorToolbox.hmyAppPath}', 'blockchain', 'latest-headers', f'--node=https://api.s0.{ourNetwork}.hmny.io']
    result_remote_shard_0 = run(remote_shard_0, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_data_shard_0 = json.loads(result_remote_shard_0.stdout)
    remote_shard = [f'{validatorToolbox.hmyAppPath}', 'blockchain', 'latest-headers', f'--node=https://api.s{ourShard}.{ourNetwork}.hmny.io']
    result_remote_shard = run(remote_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    remote_data_shard = json.loads(result_remote_shard.stdout)
    local_shard = [f'{validatorToolbox.hmyAppPath}', 'blockchain', 'latest-headers']
    result_local_shard = run(local_shard, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    local_data_shard = json.loads(result_local_shard.stdout)
    print(f"""
{stringStars()}
* Current Date & Time: {timeNow}
*
{stringStars()}
* Current Status of our server {validatorToolbox.serverHostName} currently on Shard {environ.get('SHARD')}:
*
* Shard 0 Sync Status:
* Local Server  - Epoch {local_data_shard['result']['beacon-chain-header']['epoch']} - Shard {local_data_shard['result']['beacon-chain-header']['shardID']} - Block {literal_eval(local_data_shard['result']['beacon-chain-header']['number'])}
* Remote Server - Epoch {remote_data_shard_0['result']['shard-chain-header']['epoch']} - Shard {remote_data_shard_0['result']['shard-chain-header']['shardID']} - Block {literal_eval(remote_data_shard_0['result']['shard-chain-header']['number'])}
*
{stringStars()}
    """)
    if int(ourShard) > 0:
        print(f"""
* Shard {ourShard} Sync Status:
*
* Local Server  - Epoch {local_data_shard['result']['shard-chain-header']['epoch']} - Shard {local_data_shard['result']['shard-chain-header']['shardID']} - Block {literal_eval(local_data_shard['result']['shard-chain-header']['number'])}
* Remote Server - Epoch {remote_data_shard['result']['shard-chain-header']['epoch']} - Shard {remote_data_shard['result']['shard-chain-header']['shardID']} - Block {literal_eval(remote_data_shard['result']['shard-chain-header']['number'])}
*
{stringStars()}
    """)
    shardStats(ourShard)
    input("* Validator stats completed, press ENTER to return to the main menu. ")

runStats()