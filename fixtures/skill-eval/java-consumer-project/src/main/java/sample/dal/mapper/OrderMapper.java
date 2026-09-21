package sample.dal.mapper;

import sample.dal.OrderRow;

public interface OrderMapper {

    OrderRow findOrderById(long id);
}
