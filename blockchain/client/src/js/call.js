// 引入 Web3 库
const {Web3} = require('web3');

// 使用 Infura 提供的 Sepolia 测试网络 URL
const infuraProjectId = 'b85b1201536841b19484f5f3917bcbc3';
const sepoliaUrl = `https://sepolia.infura.io/v3/${infuraProjectId}`;

// 创建 Web3 实例
const web3 = new Web3(sepoliaUrl);

// 例如，获取当前区块号
async function getBlockNumber() {
    const blockNumber = await web3.eth.getBlockNumber();
    console.log('Current Block Number:', blockNumber);
}

// 例如，发送交易
async function sendTransaction() {
    const account = '0x72555AC195E65b8448674cf4333b33B5EC0617B1';
    const privateKey = 'f69d4f20895da23b6aa689df9d92348ffeb5b24fdb7905d13966fec678646499';

    const tx = {
        from: account,
        to: '0xB78c3516EB38BbA9b0bb16D2fb9B82ceFDE90654',
        value: web3.utils.toWei('0.01', 'ether'),
        gas: 21000,
        maxPriorityFeePerGas: web3.utils.toWei('200', 'gwei'), // 设置最大优先费
        maxFeePerGas: web3.utils.toWei('3000', 'gwei'), // 设置最大费
    };

    const signedTx = await web3.eth.accounts.signTransaction(tx, privateKey);

    web3.eth.sendSignedTransaction(signedTx.rawTransaction)
        .on('receipt', console.log)
        .on('error', console.error);
}

// 调用函数
export {getBlockNumber};

