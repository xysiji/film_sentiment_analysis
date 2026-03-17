import request from '@/api/request'

const base = '/sms'


export function sendSms(data) {
  return request({
    url: base + '/sendSms',
    method: 'post',
    data
  })
}
