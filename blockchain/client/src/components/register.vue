<template>
  <el-card class="register_card">
    <el-image class="logo_image" :src="logo " fit="cover"></el-image>
    <p class="login_title">注册</p>
    <el-form ref="ruleForm" :model="form" :rules="rules">
      <el-form-item prop="username">
        <el-input
          placeholder="输入账号"
          v-model="form.username"
          prefix-icon="el-icon-user"
        />
      </el-form-item>
            <el-form-item prop="password">
        <el-input
          type="password"
          placeholder="输入密码"
          v-model="form.password"
          prefix-icon="el-icon-lock"
        />
      </el-form-item>
      <el-form-item>
        <el-button
          :loading="loginLoading"
          style="background: #5b89fe;color: white"
          @click="submitForm('ruleForm')"
          >注册</el-button>
      </el-form-item>

    </el-form>

</el-card>
</template>

<script>
export default {
    data() {
    return {
      logo: require("@/assets/logo.png"),
      form: {
        username: "",
        password: "",
      },
      loginLoading: false,
      rules: {
        username: [
          {required: true, message: "输入账号", trigger: "blur"},
        ],
        password: [
          {required: true, message: "输入密码", trigger: "blur"},
        ],
      }

    };
  },
  methods:{
      submitForm(formName) {
        this.$refs[formName].validate((valid) => {
        if (valid) {
          this.loginLoading = true;
          this.$axios
            .post("/api/register", this.$qs.stringify(this.form))
            .then((res) => {
              if (res.data.success) {
                this.$router.push("/");
                this.$message.success("注册成功！");
              } else {
                this.$message.error(res.data.msg);
                this.loginLoading = false;
              }
            })
            .catch((err) => {
              console.log(err)
              this.$message.error("服务器连接失败");
              this.loginLoading = false;
            });
        } else {
          return false;
        }
      });
      }
  }
}
</script>

<style scoped>

.login_title{
  font-size: 20px;
  font-weight: bold;
}
.logo_image{
  width: 50px;
  height: 50px;
  margin-top: 30px;
}
.register_card{
  position: absolute;
  left:0;
  right: 0;
  top: 0;
  bottom: 0;
  margin: auto;
  width: 20%;
  min-width: 300px;
  height: 400px;
  min-height: 400px;
  border-radius: 10px;
  text-align: center;
}
.el-button{
  width: 100%;
}
</style>
