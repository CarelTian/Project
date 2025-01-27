<template>
  <div>
    <el-card shadow="hover">
  <el-row type="flex" justify="space-between">
    <el-form
      ref="Form"
      :model="Form"
      size="small"
      inline="true"
      >
      <el-form-item label="区块链地址：" prop="index">
        <el-input
          v-model.trim="Form.address"
          placeholder="请输入区块链地址"
          />
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          icon="el-icon-search"
          size="small"
          @click="handleSearch()"
          ></el-button>
        <el-button
          type="primary"
          icon="el-icon-set-up"
          size="small"
          @click="back()"
          ></el-button>
      </el-form-item>
    </el-form>
  </el-row>
      <el-table ref="address":data="tableData" stripe border>
      <el-table-column prop="ID" label="虚拟财产ID" width="300"/>
      <el-table-column prop="asset" label="虚拟财产名称" />
      <el-table-column prop="node" label="认证节点" />
      <el-table-column prop="state" label="状态" />
    </el-table>

</el-card>
  </div>

</template>

<script>
export default {
  data(){
    return{
      Form:{
        address:''
      },
      tableData: [],
    };
  },
  created() {
    this.GetTable();
  },
  methods:{
    async GetTable(){
      const result = await this.$axios.get("/api/searchAsset");
      if (result.data.success) {
        this.tableData=result.data.data;
      } else {
        this.$message.error(result.data.msg);
      }
    },
    async handleSearch(){
      if(this.Form.address!=''){
        const  result= await this.$axios.get("/api/searchAsset", {
          params:this.Form});
        if (result.data.success) {
        this.tableData = result.data.data;
      } else {
        this.$message.error(result.data.message);
      }

      }

    },
    back(){
      this.Form.address='';
      this.GetTable();
    }

  }
}
</script>

<style scoped>

</style>
