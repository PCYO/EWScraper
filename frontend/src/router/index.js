import Vue from 'vue'
import Router from 'vue-router'

import EarningsWhispers from '@/components/EarningsWhispers'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'EarningsWhispers',
      component: EarningsWhispers
    }
  ]
})
