# Simplified swap without fees
import math

# LIQUIDITY
# given some amount of an asset and pair reserves, returns an equivalent amount of the other asset
# used when adding liquidity
def quote(amountA, reserveA, reserveB):
    assert(amountA > 0)
    assert(reserveA > 0 and reserveB > 0)
    amountB = (amountA * reserveB) / reserveA
    return amountB

# SWAP
# simplified version of above
def get_amount_delta(amount0_delta, reserve0, reserve1):
    dx = amount0_delta
    x = reserve0
    y = reserve1
    return (-dx*y)/(x+dx)

# Simple ERC20 token
class SimpleToken:
    def __init__(self):
        self.balance_of = {}
        self.total_supply = 0
    def _mint(self, to, value):
        self.total_supply += value
        self.balance_of[to] = self.balance_of.get(to, 0) + value
    def _burn(self, from_, value):
        self.total_supply -= value
        self.balance_of[from_] = self.balance_of.get(from_, 0) - value
    
class SimpleSwap(SimpleToken):
    def __init__(self):
        super().__init__();
        self.reserve0 = 0
        self.reserve1 = 0
    def k(self):
        return self.reserve0 * self.reserve1
    def liquidity(self):
        return math.sqrt(self.k())
    
    def mint(self, to, amount0 = None, amount1 = None):
        assert(not (amount0 is None and amount1 is None));
        if amount0 is None:
            amount0 = quote(amount1, self.reserve1, self.reserve0)
        if amount1 is None:
            amount1 = quote(amount0, self.reserve0, self.reserve1)
            
        if self.total_supply == 0:
            # first mint
            liquidity = math.sqrt(amount0 * amount1)
            # omitted min. liquidity code for simplicity
        else :
            l1 = amount0/self.reserve0 * self.total_supply
            l2 = amount1/self.reserve1 * self.total_supply
            # ensures that amounts are added in same proportion otherwise the smallest percent wins?
            liquidity = math.min(l1, l2)
        self.reserve0 += amount0
        self.reserve1 += amount1
        self._mint(to, liquidity)
        
    def swap(self, amount0_delta):
        # balance represented token reserve after a successful swap
        amount1_delta = get_amount_delta(amount0_delta, self.reserve0, self.reserve1)
        reserve0_new = self.reserve0 + amount0_delta
        reserve1_new = self.reserve1 + amount1_delta
        # assert (reserve0_new * reserve1_new == self.k()), 'k invariant is not preserved'
        self.reserve0 = reserve0_new
        self.reserve1 = reserve1_new
        return amount1_delta
    # Price of 1 token0 in token1
    def price0(self):
        return self.reserve1/self.reserve0
    # Price of 1 token1 in token0
    def price1(self):
        return self.reserve0/self.reserve1
    def reserves_priced_in_token0(self):
        return self.reserve0 + self.reserve1 * self.price1();
    def reserves_priced_in_token1(self):
        return self.reserve1 + self.reserve0 * self.price0();
    def pprint(self):
        print("k = {}".format(self.k()))
        print("lp_supply = {}".format(self.total_supply))
        print("reserve0 = {}".format(self.reserve0))
        print("reserve1 = {}".format(self.reserve1))
        print("total reserves = {} token0 aka {} token1".format(
            self.reserves_priced_in_token0(),
            self.reserves_priced_in_token1())
        )
        print("LPs = {}".format(self.balance_of))
        print("1 token0 = {} token1".format(self.price0()))
        print("1 token1 = {} token0".format(self.price1()))
