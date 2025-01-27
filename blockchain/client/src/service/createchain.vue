<template>
<div class="content">
  <el-card shadow="hover" style="width:400px">
    <el-form ref="form" :model="form":rules="rules" label-width="100px">
      <el-form-item label="区块链名称" prop="name" >
        <el-input v-model="form.name" placeholder="请输入区块链名称" ></el-input>
      </el-form-item>
      <el-form-item label ="区块链ID" prop="id">
        <el-input v-model="form.id" placeholder="请输入区块链ID"></el-input>
      </el-form-item>
      <el-form-item label ="组织名称" prop="organization">
        <el-input v-model="form.organization" placeholder="请输入组织名称"></el-input>
      </el-form-item>
      <el-form-item label ="主节点IP" prop="ip">
        <el-input v-model="form.ip" placeholder="请输入主节点IP地址"></el-input>
      </el-form-item>
      <el-form-item label ="共识算法" prop="consensus">
        <el-select
          placeholder="选择共识算法"
          style="width: 260px"
          v-model="form.category"
          :options="categoryList">
          <el-option label="Pow" value="1"></el-option>
          <el-option label="Pos" value="2"></el-option>
          <el-option label="PBFT" value="3"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit('form')">提交</el-button>
        <el-button @click="$router.go(-1)">取消</el-button>
      </el-form-item>
    </el-form>

  </el-card>
</div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        name: "",
        id: "",
        organization: "",
        category: ""
      },
      rules: {
        name: [
          {
            required: true,
            message: "请输入区块链名称",
            trigger: "blur",
          },
        ],
        id: [
          {
            required: true,
            message: "请输入区块链ID",
            trigger: "blur",
          },
        ],
        organization: [
          {
            required: true,
            message: "请输入组织名称",
            trigger: "blur",
          },
        ],
        ip:[
          {
            required:true,
            message:"请输入主节点IP",
            trigger:"blur",
          }
        ]
      },
    };
  },
  created(){
    this.form.category="PBFT";

  },
  methods:{
      onSubmit(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          let url = this.form.id ? "/course/update" : "/course/save";
          this.$axios.post(url, this.form).then((res) => {
            if (res.data.success) {
              this.$message.success("保存成功！");
              this.$router.go(-1);
            } else {
              this.$message.error(res.data.msg);
            }
          });
        } else {
          return false;
        }
      });
    },

  }
}
</script>


<style scoped>

</style>

