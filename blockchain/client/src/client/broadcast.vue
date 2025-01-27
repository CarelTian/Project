<template>
   <el-card>
     <el-row>Transaction Hex</el-row>
      <el-form
      ref="broadcast"
      :model="searchblock"
      size="small"
      inline="true"
      >
      <el-form-item  prop="a">
        <el-input
         style="width: 600px; font-size: 16px"
         type="textarea"
         rows="15"
         placeholder="请输入工具生成的交易内容"
         v-model="broadcast.content">
        </el-input>
      </el-form-item>
        <el-row></el-row>
      <el-button size="medium" icon="el-icon-s-promotion "@click="send()"
>点击广播</el-button>
    </el-form>
   </el-card>
</template>

<script>
export default {
  data(){
    return{
      broadcast:{
        content:""
      }
    };
  },
  methods:{
    send(){
      console.log(this.broadcast.content);
      let fd=new FormData();
      fd.append('content',this.broadcast.content)
      this.$axios
      .post('/api/broadcast',fd)
      .then((res)=>{
        if (res.data.success) {
          this.$message.success("广播成功！");
        } else {
          this.$message.error(res.data.msg);
        }
      })
      .catch((err) => {
        console.log(err)
              this.$message.error("服务器连接失败");
              this.loginLoading = false;
      });

    }
  }
}
</script>

<style scoped>

</style>
