import pytest
from ethereum import utils as u
import json
import os

"""
    run test with:     pytest -v
"""

ETH = 10**18
TOKEN = 10**18
EXCHANGE_ABI = os.path.join(os.path.dirname(__file__), '../ABI/exchangeABI.json')

@pytest.fixture
def uni_token(t, contract_tester):
    return contract_tester('Token/UniToken.sol', args=[])

@pytest.fixture
def swap_token(t, contract_tester):
    return contract_tester('Token/SwapToken.sol', args=[])

@pytest.fixture
def uniswap_factory(t, contract_tester):
    return contract_tester('Exchange/UniswapFactory.sol', args=[])

def test_uniswap_factory(t, uni_token, swap_token, uniswap_factory, contract_tester, assert_tx_failed):
    t.s.mine()
    # Create UNI token exchange
    uni_exchange_address = uniswap_factory.createExchange(uni_token.address)
    abi = json.load(open(EXCHANGE_ABI))
    uni_token_exchange = t.ABIContract(t.s, abi, uni_exchange_address)
    assert uniswap_factory.getExchangeCount() == 1
    assert uni_exchange_address == uniswap_factory.tokenToExchangeLookup(uni_token.address)
    assert uniswap_factory.tokenToExchangeLookup(uni_token.address) == uni_exchange_address
    assert  u.remove_0x_head(uniswap_factory.exchangeToTokenLookup(uni_exchange_address)) == uni_token.address.hex();
    # Test UNI token exchange initial state
    assert uni_token_exchange.FEE_RATE() == 500
    assert uni_token_exchange.ethInMarket() == 0
    assert uni_token_exchange.tokensInMarket() == 0
    assert uni_token_exchange.invariant() == 0
    assert uni_token_exchange.ethFees() == 0
    assert uni_token_exchange.tokenFees() == 0
    assert u.remove_0x_head(uni_token_exchange.tokenAddress()) == uni_token.address.hex()
    assert uni_token_exchange.totalShares() == 0
    t.s.mine()
    # Deploy SWAP token exchange contract with factory
    swap_exchange_address = uniswap_factory.createExchange(swap_token.address)
    swap_token_exchange = t.ABIContract(t.s, abi, swap_exchange_address)
    assert uniswap_factory.getExchangeCount() == 2
    assert swap_exchange_address == uniswap_factory.tokenToExchangeLookup(swap_token.address)
    assert uniswap_factory.tokenToExchangeLookup(swap_token.address) == swap_exchange_address
    assert  u.remove_0x_head(uniswap_factory.exchangeToTokenLookup(swap_exchange_address)) == swap_token.address.hex();
    # create exchange fails if sent ether
    assert_tx_failed(t, lambda: uniswap_factory.createExchange(uni_token.address, value=10))
    # create exchange fails if parameters are missing or empty
    assert_tx_failed(t, lambda: uniswap_factory.createExchange())
    assert_tx_failed(t, lambda: uniswap_factory.createExchange('0000000000000000000000000000000000000000'))
