with order_surplus AS (
    SELECT
        s.block_number,
        ss.winner as solver,
        s.auction_id,
        s.tx_hash,
        t.order_uid,
        o.sell_token,
        o.buy_token,
        t.sell_amount, -- the total amount the user sends
        t.buy_amount, -- the total amount the user receives
        oe.surplus_fee as observed_fee, -- the total discrepancy between what the user sends and what they would have send if they traded at clearing price
        o.kind,
        CASE
            WHEN o.kind = 'sell' THEN t.buy_amount - t.sell_amount * o.buy_amount / (o.sell_amount + o.fee_amount)
            WHEN o.kind = 'buy' THEN t.buy_amount * (o.sell_amount + o.fee_amount) / o.buy_amount - t.sell_amount
        END AS surplus,
        CASE
            WHEN o.kind = 'sell' THEN o.buy_token
            WHEN o.kind = 'buy' THEN o.sell_token
        END AS surplus_token
    FROM
        settlements s
        JOIN settlement_scores ss -- contains block_deadline
        ON s.auction_id = ss.auction_id
        JOIN trades t -- contains traded amounts
        ON s.block_number = t.block_number -- log_index cannot be checked, does not work correctly with multiple auctions on the same block
        JOIN orders o -- contains tokens and limit amounts
        ON t.order_uid = o.uid
        JOIN order_execution oe -- contains surplus fee
        ON t.order_uid = oe.order_uid
        AND s.auction_id = oe.auction_id
    WHERE owner = '\xb3861b445F873AeE9a5a4e1E2957d679Bc91B9E2' --COW_AMM_ADDRES here GNO
    and s.block_number >= 32236569 --START_BLOCK
),
order_protocol_fee AS (
    SELECT
        os.block_number,
        os.auction_id,
        os.solver,
        os.tx_hash,
        os.sell_amount,
        os.buy_amount,
        os.sell_token,
        os.observed_fee,
        os.surplus,
        os.surplus_token,
        CASE
            WHEN fp.kind = 'surplus' THEN CASE
                WHEN os.kind = 'sell' THEN
                -- We assume that the case surplus_factor != 1 always. In
                -- that case reconstructing the protocol fee would be
                -- impossible anyways. This query will return a division by
                -- zero error in that case.
                LEAST(
                    fp.surplus_max_volume_factor * os.sell_amount * os.buy_amount / (os.sell_amount - os.observed_fee),
                    -- at most charge a fraction of volume
                    fp.surplus_factor / (1 - fp.surplus_factor) * surplus -- charge a fraction of surplus
                )
                WHEN os.kind = 'buy' THEN LEAST(
                    fp.surplus_max_volume_factor / (1 + fp.surplus_max_volume_factor) * os.sell_amount,
                    -- at most charge a fraction of volume
                    fp.surplus_factor / (1 - fp.surplus_factor) * surplus -- charge a fraction of surplus
                )
            END
            WHEN fp.kind = 'volume' THEN fp.volume_factor / (1 + fp.volume_factor) * os.sell_amount
        END AS protocol_fee,
        CASE
            WHEN fp.kind = 'surplus' THEN os.surplus_token
            WHEN fp.kind = 'volume' THEN os.sell_token
        END AS protocol_fee_token
    FROM
        order_surplus os
        JOIN fee_policies fp -- contains protocol fee policy
        ON os.auction_id = fp.auction_id
        AND os.order_uid = fp.order_uid
),
order_protocol_fee_prices AS (
    SELECT
        opf.block_number,
        opf.solver,
        opf.tx_hash,
        opf.surplus,
        opf.protocol_fee,
        opf.protocol_fee_token,
        CASE
            WHEN opf.sell_token != opf.protocol_fee_token THEN opf.observed_fee - (opf.sell_amount - opf.observed_fee) / opf.buy_amount * opf.protocol_fee
            ELSE opf.observed_fee - opf.protocol_fee
        END AS network_fee,
        opf.sell_token as network_fee_token,
        ap_surplus.price / pow(10, 18) as surplus_token_price,
        ap_protocol.price / pow(10, 18) as protocol_fee_token_price,
        ap_sell.price / pow(10, 18) as network_fee_token_price
    FROM
        order_protocol_fee opf
        JOIN auction_prices ap_sell -- contains price: sell token
        ON opf.auction_id = ap_sell.auction_id
        AND opf.sell_token = ap_sell.token
        JOIN auction_prices ap_surplus -- contains price: surplus token
        ON opf.auction_id = ap_surplus.auction_id
        AND opf.surplus_token = ap_surplus.token
        JOIN auction_prices ap_protocol -- contains price: protocol fee token
        ON opf.auction_id = ap_protocol.auction_id
        AND opf.protocol_fee_token = ap_protocol.token
)
select
    sum(surplus * surplus_token_price) / pow(10, 18) as surplus_eth,
    sum(protocol_fee * protocol_fee_token_price) / pow(10, 18) as protocol_fee_eth,
    sum(network_fee * network_fee_token_price) / pow(10, 18) as network_fee_eth
from order_protocol_fee_prices