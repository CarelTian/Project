import Vue from 'vue'
import Router from 'vue-router'
import login from "../components/login";
import register from "../components/register";
import createchain from "../service/createchain";
import node from "../service/node";
import admin from "../service/admin";
import accept from "../service/accept";
import block from "../components/block";
import property from "../components/property";
import commit from "../service/commit";
import uploadAsset from "../client/uploadAsset";
import broadcast from "../client/broadcast";
import asset from "../client/asset";
import home from "../client/home.vue";


Vue.use(Router)
/*
router.beforeEach((to,from,next) =>{
  if(to.path=='/'){
    return next()
  }
  const tokenStr=sessionStorage.getItem('token')
  if(!tokenStr){
    return next('/')
  }else {
    next()
  }
})
*/
export default new Router({
  mode:"history",
  routes: [
    {
      path: '/',
      component:home,
      name:'home',

    },
    {
      path: '/register',
      component:register,
      name:'register',
    },
    {
      path: '/admin',
      component:admin,
      name:'admin',
      children:[{
        path: '/create/blockchain',
        component:createchain,
      }, {
      path :'/admin/node',
      component :node
     }, {
        path:'/admin/accept',
        component:accept
      },{
        path:'/admin/block',
        component:block,
      },  {
      path:'/admin/property',
      component:property,
      name:'property'
    }, {
      path:'/admin/commit',
      component:commit,
      name:'commit'
    },
      ]
    },
    {
      path:'/home',
      component: ()=>import('../client/home'),
      name:'home',
      children:[{
        path: '/home/block',
        component:block
      },{
        path: '/home/property',
        component :property
      },{
        path: '/home/upload',
        component :uploadAsset
      },{
        path: '/home/broadcast',
        component :broadcast
      },{
        path: '/home/asset',
        component: asset
      }
      ]
    },
  ]

})
