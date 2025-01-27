<template>
<div classs="content">
  <el-card shadow="hover">
    <el-row class="rowSpace">
        <el-col :span="8">
        </el-col>
    </el-row>
    <el-table ref="table":data="tableData" stripe border>
      <el-table-column type="index" label="序号" width="50px"/>
      <el-table-column prop="MD5" label="MD5" width="250px"/>
      <el-table-column prop="address" label="区块链地址" width="300px"/>
      <el-table-column prop="type" label="财产类型" />
      <el-table-column prop="asset" label="财产名称" />
       <el-table-column prop="node" align="center" label="认证节点" >
       </el-table-column>
    </el-table>
  </el-card>
</div>
</template>

<script>
  export default {
    data(){
      return{
        tableData:[]
      }
    },
    created(){
      this.GetTable();
    },
    methods:{
      async GetTable(){
      const result = await this.$axios.get("/api/my");
      if (result.data.success) {
        this.tableData=result.data.data;
      } else {
        this.$message.error(result.data.msg);
      }

    }

    }
  }
</script>

<style scoped>

</style>
