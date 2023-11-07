# Programming language - Python

class Order:

    no_of_orders = 0
    transactions_history = []
    shares_acquired, shares_sold = {}, {}   # to keep bought and sold shares at specific price

    def __init__(self, order, order_type, price, quantity):

        print('_' * 10 + 'New order' + '_' * 10)
        self.id = Order.no_of_orders        # just to provide auto-incerement id
        Order.no_of_orders += 1
        self.order = order
        self.price = price
        self.quantity = quantity
        self.order_type = order_type
        Order.archive_orders(self)          # to store all orders in a list

        if self.order == 'Buy':
            if self.order_type == 'Add':
                Order.add_acquire(self)
            if self.order_type == 'Remove':
                Order.remove_acquire(self)

        if self.order == 'Sell':
            if self.order_type == 'Add':
                Order.add_sell(self)
            if self.order_type == 'Remove':
                Order.remove_sell(self)

        Order.display_best_prices()         # displaying sum of buy/sell orders iwth prices in every step.

    def archive_orders(self):
        Order.transactions_history.append(self)

    def add_acquire(self):
        if Order.shares_acquired.get(self.price):
            Order.shares_acquired[self.price] += self.quantity
        else:
            Order.shares_acquired[self.price] = self.quantity

    def add_sell(self):
        if Order.shares_sold.get(self.price):
            Order.shares_sold[self.price] += self.quantity
        else:
            Order.shares_sold[self.price] = self.quantity

    def remove_acquire(self):
        if Order.shares_acquired.get(self.price):
            Order.shares_acquired[self.price] -= self.quantity
            if Order.shares_acquired[self.price] == 0:
                del Order.shares_acquired[self.price]
        else:
            print('You cannot remove order, that had not been done!')

    def remove_sell(self):
        if Order.shares_sold.get(self.price):
            Order.shares_sold[self.price] -= Order.shares_sold[self.quantity]
            if Order.shares_sold[self.price] == 0:
                del Order.shares_sold[self.price]
        else:
            print('You cannot remove order, that had not been done!')

    @staticmethod
    def best_price_buy():
        if Order.shares_acquired:
            best_buy_price = min(Order.shares_acquired.items(), key=lambda k: k[0])[0]
            best_buy_quantity = Order.shares_acquired[best_buy_price]
            return f'So far your best buy is {best_buy_quantity} shares at a price of {best_buy_price}.'
        else:
            return 'No acquisition have been made so far.'

    @staticmethod
    def best_sell_quantity():
        if Order.shares_sold:
            best_sell_price = max(Order.shares_sold.items(), key=lambda k: k[0])[0]
            best_sell_quantity = Order.shares_sold[best_sell_price]
            return f'So far your best sell is {best_sell_quantity} shares at a price of {best_sell_price}.'
        else:
            return 'No sales have been made so far.'

    @staticmethod
    def display_best_prices():
        print(Order.best_price_buy())
        print(Order.best_sell_quantity())


def main():
    # Type your own orders to check if code works fine.
    order1 = Order('Buy', 'Add', 20, 100)
    order2 = Order('Buy', 'Remove', 20, 100)
    order3 = Order('Buy', 'Add', 23, 50)
    order4 = Order('Buy', 'Add', 23, 70)
    order5 = Order('Buy', 'Remove', 23, 50)
    order6 = Order('Sell', 'Add', 28, 100)
    order7 = Order('Buy', 'Remove', 20, 100)


if __name__ == '__main__':
    main()
