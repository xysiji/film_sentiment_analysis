import request from '@/api/request'

const base = '/alipay'


export function pay(data) {
  return request({
    url: base + '/pay',
    method: 'post',
    data
  })
}
