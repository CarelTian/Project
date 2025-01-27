<template>
  <div>
    <el-container class="home-container">
      <!-- header -->
      <el-header>
        <el-row>
          <el-col :span="4">
            <p class="system-name">客户端</p>
          </el-col>
          <el-col :offset="12" :span="8" style="min-width: 150px">
            <el-dropdown  style="float: right; margin: 20px 10px" trigger="click">
              <span
                class="el-dropdown-link"
                style="color: #fff; cursor: pointer"
              >
               {{user}} &nbsp;&nbsp;<i class="fa fa-caret-down fa-1x"></i>
              </span>
             <el-dropdown-menu slot="dropdown">
                <el-dropdown-item @click.native="logout()"
                  >退出系统</el-dropdown-item>
             </el-dropdown-menu>
            </el-dropdown>
          </el-col>
        </el-row>
      </el-header>

      <el-container style="overflow: auto">
        <!-- 菜单 -->
        <el-aside>
          <div class="toggle-button" @click="isCollapse = !isCollapse">
            <i v-if="isCollapse" class="el-icon-s-unfold"></i>
            <i v-if="!isCollapse" class="el-icon-s-fold"></i>
          </div>
          <el-menu
            router
            :default-active="activePath"
            class="el-menu-vertical-demo"
            :collapse="isCollapse"
          >
            <el-menu-item  @click="saveActiveNav('/index')">
              <i class="el-icon-house"></i>
              <span slot="title">首页</span>
            </el-menu-item>
            <el-menu-item
              index="/home/asset"
              @click="saveActiveNav('/user/list')"
               >
              <i class="el-icon-user"></i>
              <span slot="title">我的资产</span>
            </el-menu-item>
            <el-menu-item index="/home/block">

                <i class="el-icon-setting"></i>
                <span>区块查询</span>
             </el-menu-item>
            <el-menu-item
              index="/home/property"
              @click="saveActiveNav('/home/property')"
            >
              <i class="el-icon-notebook-1"></i>
              <span slot="title"> 虚拟财产查询</span>
            </el-menu-item>
            <el-menu-item index="/home/upload">
              <i class="el-icon-tickets"></i>
              <span slot="title">上传虚拟财产</span>
            </el-menu-item>

            <el-menu-item index="/home/broadcast">
              <i class="el-icon-reading"></i>
              <span slot="title">广播交易</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-container>
          <el-main>
            <!-- 主要内容 -->
            <router-view></router-view>
          </el-main>
          <el-footer>毕业设计</el-footer>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      user:"",
      isCollapse: false,
      // 被激活的链接地址,默认是首页
      activePath: "",
      editPasswordDialog: false,
      editPasswordForm: {
        oldPassword: "",
        newPassword: "",
        confirmPassword: "",
      },
    };
  },
  created() {
    this.user=sessionStorage.getItem('user');
    this.activePath = sessionStorage.getItem("activePath")
      ? sessionStorage.getItem("activePath")
      : "/index";

  },
  methods: {
    // 保存链接的激活状态
    saveActiveNav(activePath) {
      sessionStorage.setItem("activePath", activePath);
      this.activePath = activePath;
    },
    // 取消关闭密码
    closeEditPassword() {
      this.editPasswordDialog = false;
      // 坑：resetFields 方法只能重置带有 props 属性的元素
      this.$refs.editPasswordForm.resetFields();
    },
    // 退出系统
    logout() {
      this.$confirm("确定要退出系统吗?", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      })
        .then(() => {
          // 清除缓存
          sessionStorage.clear();
          this.$router.push("/");
        })
        .catch(() => {
          return false;
        });
    },
  },
};
</script>

<style  scoped>
.home-container {
  position: absolute;
  height: 100%;
  top: 0px;
  left: 0px;
  width: 100%;
  background: #f2f3f5;
  opacity: 1;
}

.el-header {
  background: #0887c2;
  padding: 0 10px;
  overflow: hidden;
}

.system-name {
  color: #fff;
  font-size: 18px;
}

.el-aside {
  background: white;
  width: auto !important;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.el-footer {
  color: #4a00f3;
  text-align: center;
  line-height: 60px;
}

.el-footer:hover {
  color: #3866d9;
}

.toggle-button {
  background-color: #d9e0e7;
  font-size: 18px;
  line-height: 24px;
  color: #fff;
  text-align: center;
  letter-spacing: 0.2em;
  cursor: pointer;
  color: black;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}


</style>
