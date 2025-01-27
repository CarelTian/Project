<template>
<div class="content">
  <el-card shadow="hover">
  <el-tag type="danger" effect="dark" size="medium" maw>待确认</el-tag>
      <el-table ref="Ninfo":data="tableData" style="margin-top: 20px" stripe border>
      <el-table-column type="index" label="序号" width="50px" />
      <el-table-column prop="name" label="用户名" width="120px"/>
      <el-table-column prop="address" label="区块链地址" width="300px"/>
       <el-table-column prop="type" label="财产类型" width="100px"/>
       <el-table-column prop="asset" label="财产名称" />
       <el-table-column prop="filename" label="文件名" />
       <el-table-column prop="option" align="center" label="操作" width="180px">
         <template slot-scope="scope">
            <el-button
              type="success"
              size="small"
              @click="accept(scope.row)"
              >接受</el-button
            >
            <el-button
              type="danger"
              size="small"
              @click="dele(scope.row)"
              >拒绝</el-button
            >
          </template>
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

    };
  },
  created() {
    this.GetTable();

  },
  methods:{
    accept(row){
      let fd=new FormData();
      fd.append('op','accept')
      fd.append('username',row.name)
      fd.append('filename',row.filename)
      fd.append('asset',row.asset)
      let index=null;
      index=this.tableData.findIndex(item=>{
        if(item.name==row.name && item.filename==row.filename&&item.asset==row.asset) return true
      })
      this.$axios.post("/api/audit", fd).then((res) => {
            if (res.data.success) {
              this.$message.success("操作成功！");
              this.tableData.splice(index,1);
            } else {
              this.$message.error(res.data.msg);
            }
      });

    },
    dele(row){
      let fd=new FormData();
      fd.append('op','delete')
      fd.append('username',row.name)
      fd.append('filename',row.filename)
      fd.append('asset',row.asset)
      let index=null;
      index=this.tableData.findIndex(item=>{
        if(item.name==row.name &&item.filename==row.filename&&item.asset==row.asset) return true
      })
      this.$axios.post("/api/audit", fd).then((res) => {
            if (res.data.success) {
              this.$message.success("操作成功！");
              this.tableData.splice(index,1);
            } else {
              this.$message.error(res.data.msg);
            }
          });
    },
    async GetTable(){
      const result = await this.$axios.get("/api/audit");
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

</style>
