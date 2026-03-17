import request from '@/api/request'

const base = '/order'


export function addOrder(data) {
  return request({
    url: base + '/add',
    method: 'post',
    data
  })
}
