import React, { useState, useEffect } from 'react';
import { Table } from 'antd';
import PropTypes from 'prop-types';

export default function FullTable({ refresh, onRefresh }) {
  const [inventoryData, setInventoryData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/get_inventory')
      .then((res) => res.json())
      .then((data) => {
        const dataWithKey = data.map((item, index) => ({
          ...item,
          key: index,
        }));
        setInventoryData(dataWithKey);
        setLoading(false);
      });
    // eslint-disable-next-line no-sparse-arrays
  }, [, refresh, onRefresh]);

  const columns = [
    {
      title: 'Item',
      dataIndex: 'itemName',
      key: 'itemName',
      sorter: (a, b) => a.itemName.localeCompare(b.itemName),
    },
    {
      title: 'Quantity',
      dataIndex: 'itemCount',
      key: 'itemCount',
      sorter: (a, b) => a.itemCount - b.itemCount,
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      filters: [
        {
          text: 'Foodstuff',
          value: 'Foodstuff',
        },
        {
          text: 'Personal Care Product',
          value: 'PersonalCareProduct',
        },
      ],
      onFilter: (value, record) => record.category.includes(value),
    },
  ];

  return (
    <>
      {loading && <h1>Please wait...</h1>}
      <Table
        dataSource={inventoryData}
        columns={columns}
        loading={loading}
        pagination={{
          defaultPageSize: 10,
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '30'],
        }}
      />
    </>
  );
}

FullTable.propTypes = {
  refresh: PropTypes.bool.isRequired,
  onRefresh: PropTypes.func.isRequired,
};
