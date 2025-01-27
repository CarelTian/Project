<template>
<div classs="content">
  <el-card shadow="hover">
    <el-tag type="success" effect="dark" size="medium" maw>已审核</el-tag>
    <el-row class="rowSpace">
        <el-col :span="8">
        </el-col>
    </el-row>
    <el-table ref="table":data="tableData" stripe border>
      <el-table-column type="index" label="序号" width="50px"/>
      <el-table-column prop="name" label="用户名" />
      <el-table-column prop="address" label="区块链地址" width="300px"/>
      <el-table-column prop="type" label="财产类型" />
      <el-table-column prop="asset" label="财产名称" />
       <el-table-column prop="filename" align="center" label="文件名" >
       </el-table-column>
    </el-table>
  </el-card>

</div>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      tableData: [{
        name:"",
        address:"",
        type:"",
        asset:"",
        filename:""
      }],

    };
  },
  created() {
     this.GetTable();
  },
  methods: {
    async GetTable(){
      const result = await this.$axios.get("/api/show");
      if (result.data.success) {
        this.tableData=result.data.data;
        console.log("new",this.tableData)
      } else {
        this.$message.error(result.data.msg);
      }

    }

  }
}



</script>

<style scoped>
.el-table {
  margin: 20px 0px;
}
</style>
